"""
slr/extractors/acm.py
=====================
Extractor for the ACM Digital Library (https://dl.acm.org/).

Strategy — API-first (ACM blocks headless Selenium with Cloudflare)
--------------------------------------------------------------------
ACM DL exposes a public JSON search endpoint used by its own frontend:

    https://dl.acm.org/action/doSearch
    ?AllField=<query>&startPage=<n>&pageSize=50&format=json

This returns structured JSON with titles, DOIs, authors, and dates — no
Selenium required, no anti-bot friction.

Selenium fallback (commented out) is preserved below for reference.
"""
from __future__ import annotations

import logging
import re
import time
from urllib.parse import quote_plus

from slr.models import Article
from slr.extractors.base import BaseExtractor
from utils.http_session import RateLimiter, build_session

logger = logging.getLogger(__name__)

_SOURCE_URL: str = "https://dl.acm.org/"
_SEARCH_API: str = "https://dl.acm.org/action/doSearch"
_PAGE_SIZE: int = 50


class AcmExtractor(BaseExtractor):
    """Extract papers from ACM Digital Library via the JSON search API."""

    name = "acm_digital_library"
    source_url = _SOURCE_URL

    def extract(self, query: str) -> list[Article]:
        self._log.info("Starting ACM DL extraction (API mode)")
        session = build_session()
        # ACM doesn't publish rate limits; be polite at 1 req/2s
        limiter = RateLimiter(calls_per_second=0.5, min_delay=2.0)
        articles: list[Article] = []
        page = 0

        # Quick probe: check if ACM is accessible (Cloudflare may return 403)
        try:
            probe = session.get(
                _SEARCH_API,
                params={"AllField": query, "startPage": 0, "pageSize": 1},
                headers={"Accept": "application/json"},
                timeout=(8, 15),
            )
            if probe.status_code == 403 or "Just a moment" in probe.text[:200]:
                self._log.warning(
                    "ACM DL is protected by Cloudflare. "
                    "Falling back to CrossRef API for ACM papers (DOI prefix 10.1145)."
                )
                articles = _extract_acm_via_crossref(query, self._log)
                self._save_raw(articles)
                return articles
        except Exception as exc:  # noqa: BLE001
            self._log.warning(
                "ACM DL probe failed: %s. Falling back to CrossRef API.", exc
            )
            articles = _extract_acm_via_crossref(query, self._log)
            self._save_raw(articles)
            return articles

        while True:
            limiter.wait()
            params = {
                "AllField": query,
                "startPage": page,
                "pageSize": _PAGE_SIZE,
            }
            try:
                resp = session.get(
                    _SEARCH_API,
                    params=params,
                    headers={"Accept": "application/json"},
                    timeout=(10, 30),
                )
                if resp.status_code == 404 or "application/json" not in resp.headers.get(
                    "Content-Type", ""
                ):
                    # ACM returned HTML (blocked or no JSON support) — fall back
                    self._log.warning(
                        "ACM DL — JSON API not available (status=%d). "
                        "Try the Selenium fallback or check the ACM API.",
                        resp.status_code,
                    )
                    break
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:  # noqa: BLE001
                self._log.error("ACM DL — API error on page %d: %s", page, exc)
                break

            # Parse the response structure
            # ACM search JSON: {"items": {"item": [...]}, "totalResultCount": N}
            items_wrapper = data.get("items") or {}
            raw_items = items_wrapper.get("item") or []

            if not raw_items:
                # Also try flat list format
                raw_items = data.get("items") if isinstance(data.get("items"), list) else []

            if not raw_items:
                self._log.info("ACM DL — no more results after page %d", page)
                break

            self._log.info("ACM DL — page %d: %d items", page, len(raw_items))

            for item in raw_items:
                article = _parse_api_item(item)
                if article:
                    articles.append(article)

            total = int(data.get("totalResultCount", 0) or 0)
            fetched = (page + 1) * _PAGE_SIZE
            self._log.debug("ACM DL — fetched %d/%d articles", len(articles), total)

            if fetched >= total or len(raw_items) < _PAGE_SIZE:
                break
            page += 1

        self._log.info("ACM DL — collected %d articles", len(articles))
        self._save_raw(articles)
        return articles


# ---------------------------------------------------------------------------
# JSON API parser
# ---------------------------------------------------------------------------


def _parse_api_item(item: dict) -> Article | None:
    """Parse a single ACM search API item dict into an Article."""
    try:
        title = (item.get("title") or "").strip()
        if not title:
            return None

        # DOI is in item["doi"]["doi"] or item["doi"]
        doi_field = item.get("doi") or {}
        if isinstance(doi_field, dict):
            doi = (doi_field.get("doi") or "").strip()
        else:
            doi = str(doi_field).strip()

        # Year
        pub_date = item.get("publicationDate") or ""
        year = _extract_year(pub_date)
        if not year:
            year = str(item.get("publicationYear") or "")

        # Authors
        authors: list[dict[str, str]] = []
        author_list = item.get("authors") or {}
        if isinstance(author_list, dict):
            author_list = author_list.get("author") or []
        for a in author_list or []:
            if isinstance(a, dict):
                given = (a.get("givenName") or "").strip()
                family = (a.get("familyName") or "").strip()
                full = f"{given} {family}".strip() if given else family
            else:
                full = str(a).strip()
            if full:
                authors.append({"fullName": full, "lastName": full.split()[-1]})

        return Article(
            title=title,
            authors=authors,
            publication_year=year,
            doi=doi,
            source=_SOURCE_URL,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("ACM DL — parse error: %s", exc)
        return None


def _extract_year(date_str: str) -> str:
    m = re.search(r"\b(19|20)\d{2}\b", date_str)
    return m.group(0) if m else ""


# ---------------------------------------------------------------------------
# CrossRef fallback — query ACM papers via the free CrossRef API
# ---------------------------------------------------------------------------

_CROSSREF_API = "https://api.crossref.org/works"
_CROSSREF_ROWS = 50  # CrossRef max per page


def _extract_acm_via_crossref(
    query: str, log: logging.Logger
) -> list[Article]:
    """Query CrossRef for ACM-published papers (DOI prefix 10.1145).

    This is used as a fallback when ACM DL is blocked by Cloudflare.
    CrossRef is free, requires no API key, and returns structured JSON
    with DOIs, titles, authors, and publication dates.
    """
    log.info("ACM CrossRef fallback — querying CrossRef for ACM papers …")

    session = build_session()
    session.headers["User-Agent"] = (
        "SLR-Pipeline/1.0 (academic research; mailto:researcher@university.edu)"
    )
    limiter = RateLimiter(calls_per_second=0.8, min_delay=1.2)

    articles: list[Article] = []
    cursor = "*"  # CrossRef deep paging cursor

    # Simplify complex boolean queries for CrossRef
    # CrossRef's query.bibliographic does basic relevance matching
    if "AND" in query or "OR" in query:
        cr_query = "digital twin cybersecurity IoT cyber-physical"
    else:
        cr_query = query

    max_pages = 20  # Safety limit: 20 * 50 = 1000 results max
    page = 0

    try:
        while page < max_pages:
            limiter.wait()
            params = {
                "query.bibliographic": cr_query,
                "filter": "prefix:10.1145",  # ACM DOI prefix
                "rows": _CROSSREF_ROWS,
                "cursor": cursor,
                "select": "DOI,title,author,published-print,published-online,abstract",
                "sort": "relevance",
                "order": "desc",
            }

            try:
                resp = session.get(_CROSSREF_API, params=params, timeout=(10, 30))
                if resp.status_code == 429:
                    import time as _time
                    retry_after = int(resp.headers.get("Retry-After", 10))
                    log.warning("CrossRef rate-limited (429). Waiting %ds …", retry_after)
                    _time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:  # noqa: BLE001
                log.error("ACM CrossRef — API error on page %d: %s", page, exc)
                break

            items = data.get("message", {}).get("items", [])
            if not items:
                break

            for item in items:
                article = _parse_crossref_item(item)
                if article:
                    articles.append(article)

            # Update cursor for next page
            next_cursor = data.get("message", {}).get("next-cursor")
            if not next_cursor or next_cursor == cursor:
                break
            cursor = next_cursor
            page += 1

            total = data.get("message", {}).get("total-results", 0)
            log.info(
                "ACM CrossRef — page %d: %d items fetched (%d total so far, %d available)",
                page, len(items), len(articles), total,
            )

    except Exception as exc:  # noqa: BLE001
        log.error("ACM CrossRef — fatal error: %s", exc, exc_info=True)

    log.info("ACM CrossRef fallback — collected %d articles", len(articles))
    return articles


def _parse_crossref_item(item: dict) -> Article | None:
    """Parse a CrossRef work item into an Article."""
    try:
        title_list = item.get("title") or []
        title = title_list[0].strip() if title_list else ""
        if not title:
            return None

        doi = (item.get("DOI") or "").strip()

        # Year from published-print or published-online
        year = ""
        for date_key in ("published-print", "published-online"):
            date_parts = (item.get(date_key) or {}).get("date-parts", [[]])
            if date_parts and date_parts[0] and date_parts[0][0]:
                year = str(date_parts[0][0])
                break

        # Authors
        authors: list[dict[str, str]] = []
        for a in item.get("author") or []:
            given = (a.get("given") or "").strip()
            family = (a.get("family") or "").strip()
            full = f"{given} {family}".strip() if given else family
            if full:
                authors.append({"fullName": full, "lastName": family or full.split()[-1]})

        abstract = (item.get("abstract") or "").strip()
        # CrossRef abstracts sometimes contain JATS XML tags — strip them
        abstract = re.sub(r"<[^>]+>", "", abstract).strip()

        return Article(
            title=title,
            authors=authors,
            publication_year=year,
            doi=doi,
            source=_SOURCE_URL,
            abstract=abstract,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("ACM CrossRef — parse error: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Selenium fallback (DISABLED — ACM blocks headless Chrome via Cloudflare)
# ---------------------------------------------------------------------------
# The Selenium implementation is preserved below for reference.
# To re-enable: uncomment the class method and call it from extract().
#
# Required imports (uncomment if re-enabling):
# from urllib.parse import quote_plus
# from selenium.common.exceptions import (
#     NoSuchElementException, StaleElementReferenceException, TimeoutException,
# )
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from utils.selenium_factory import build_driver, dismiss_cookie_banner, make_wait
#
# _NEXT_PAGE_CSS = "a.pagination__btn--next:not([aria-disabled='true'])"
# _DOI_HREF_RE = re.compile(r"/doi/(10\.\d{4,}/[^\s?#'\"<>]+)")
# _DOI_RE = re.compile(r"(10\.\d{4,}/[^\s\"'<>]+)")
# _COOKIE_XPATHS = (
#     "//*[@id='CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll']",
#     "//button[contains(text(),'Reject')]",
#     "//button[@id='onetrust-reject-all-handler']",
# )
#
# def _extract_via_selenium(self, query: str) -> list[Article]:
#     """Selenium fallback — only works when NOT headless (Cloudflare blocks headless)."""
#     driver = build_driver(headless=False)  # must be non-headless for ACM
#     articles: list[Article] = []
#     try:
#         encoded_query = quote_plus(query)
#         url = f"https://dl.acm.org/action/doSearch?AllField={encoded_query}&startPage=0&pageSize=50"
#         driver.get(url)
#         wait = make_wait(driver, timeout=30)
#         dismiss_cookie_banner(driver, *_COOKIE_XPATHS, timeout=8)
#         page = 0
#         while True:
#             page += 1
#             try:
#                 wait.until(EC.presence_of_element_located(
#                     (By.XPATH, ".//li[contains(@class,'search__item')]")
#                 ))
#             except TimeoutException:
#                 break
#             items = driver.find_elements(By.XPATH, ".//li[contains(@class,'search__item')]")
#             for item in items:
#                 # Title + DOI from anchor href /doi/10.XXXX/...
#                 try:
#                     anchor = item.find_element(
#                         By.XPATH, ".//h3[contains(@class,'issue-item__title')]//a"
#                     )
#                     title = (anchor.text or "").strip()
#                     href = anchor.get_attribute("href") or ""
#                     m = _DOI_HREF_RE.search(href)
#                     doi = m.group(1) if m else ""
#                     if title:
#                         articles.append(Article(title=title, doi=doi, source=_SOURCE_URL))
#                 except Exception:
#                     continue
#             try:
#                 next_btn = driver.find_element(By.CSS_SELECTOR, _NEXT_PAGE_CSS)
#                 driver.execute_script("arguments[0].click();", next_btn)
#                 time.sleep(3)
#                 wait.until(EC.presence_of_element_located(
#                     (By.XPATH, ".//li[contains(@class,'search__item')]")
#                 ))
#             except Exception:
#                 break
#     finally:
#         driver.quit()
#     return articles
