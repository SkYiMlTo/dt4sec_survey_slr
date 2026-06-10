"""
slr/extractors/springer.py
==========================
Extractor for Springer Link (https://link.springer.com/).

Strategy — API-only (key confirmed working 2026-06-03)
------------------------------------------------------
Uses the Springer Nature OpenAccess API
(``api.springernature.com/openaccess/json``).

Requires the ``SPRINGER_API_KEY`` environment variable (set in .env or
as a GitHub Actions secret).  If the key is absent the extractor logs a
warning and returns an empty list rather than falling back to Selenium,
since the API key is now confirmed available and the Selenium path is
fragile by comparison.

Rate limits (Open Access API, free tier):
    - 100 requests / minute
    - 500 requests / day
    - We target 1.5 req/s (~90/min) to stay safely under the per-minute cap.

Key improvements over the legacy version
-----------------------------------------
- No bare ``except: pass``
- DOI extracted from structured JSON ``doi`` field (never from href scraping)
- Proper pagination via ``s`` (start) + ``total``
- Per-request rate limiting
- Authors, year, and abstract included in every record

Selenium fallback
-----------------
The original Selenium-based fallback is preserved below (commented out) for
reference.  Re-enable it by uncommenting ``_extract_via_selenium`` and
restoring the ``else`` branch in ``extract()``.
"""
from __future__ import annotations

import logging
import os
import re
import time
from urllib.parse import urlencode

from slr.models import Article
from slr.extractors.base import BaseExtractor
from utils.http_session import RateLimiter, build_session

logger = logging.getLogger(__name__)

_SOURCE_URL: str = "https://link.springer.com/"
_API_BASE: str = "https://api.springernature.com/openaccess/json"
_PAGE_SIZE: int = 25  # Springer API max per page


class SpringerExtractor(BaseExtractor):
    """Extract papers from Springer Link via the Open Access API."""

    name = "springer_link"
    source_url = _SOURCE_URL

    def extract(self, query: str) -> list[Article]:
        api_key = os.getenv("SPRINGER_API_KEY", "").strip()
        if not api_key:
            self._log.warning(
                "Springer — SPRINGER_API_KEY is not set. "
                "Add it to your .env file or GitHub Actions secrets. "
                "Skipping Springer extraction."
            )
            return []

        self._log.info("Springer — using Open Access API")
        articles = self._extract_via_api(query, api_key)

        # ── Selenium fallback (disabled — API key is now in use) ──────────
        # To re-enable: remove the ``if not api_key`` early return above and
        # restore the else branch calling ``self._extract_via_selenium(query)``.
        # ─────────────────────────────────────────────────────────────────────

        self._log.info("Springer — collected %d articles", len(articles))
        self._save_raw(articles)
        return articles

    # ------------------------------------------------------------------
    # API strategy (active)
    # ------------------------------------------------------------------

    def _extract_via_api(self, query: str, api_key: str) -> list[Article]:
        """Paginate through Springer Nature OpenAccess API results."""
        session = build_session()
        # 100 req/min = ~1.66 req/s. We target 1.5 to stay safely under.
        limiter = RateLimiter(calls_per_second=1.5, min_delay=0.67)
        articles: list[Article] = []
        start = 1

        while True:
            params = {
                "q": query,
                "api_key": api_key,
                "p": _PAGE_SIZE,
                "s": start,
                "sort": "relevance",
            }
            url = f"{_API_BASE}?{urlencode(params)}"
            limiter.wait()

            try:
                resp = session.get(url, timeout=(10, 30))
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:  # noqa: BLE001
                self._log.error("Springer API error at offset %d: %s", start, exc)
                break

            records = data.get("records", [])
            if not records:
                break

            for rec in records:
                article = _parse_api_record(rec)
                if article:
                    articles.append(article)

            total = int(data.get("result", [{}])[0].get("total", 0))
            self._log.debug(
                "Springer API — fetched %d/%d articles", len(articles), total
            )

            start += _PAGE_SIZE
            if start > total:
                break

        return articles

    # ------------------------------------------------------------------
    # Selenium strategy (DISABLED — kept for reference only)
    # ------------------------------------------------------------------
    #
    # def _extract_via_selenium(self, query: str) -> list[Article]:
    #     from selenium.common.exceptions import (
    #         NoSuchElementException,
    #         TimeoutException,
    #     )
    #     from selenium.webdriver.common.by import By
    #     from selenium.webdriver.common.keys import Keys
    #     from selenium.webdriver.support import expected_conditions as EC
    #
    #     from utils.selenium_factory import (
    #         build_driver,
    #         dismiss_cookie_banner,
    #         make_wait,
    #     )
    #
    #     driver = build_driver()
    #     articles: list[Article] = []
    #
    #     _COOKIE_XPATHS = (
    #         "//button[contains(@class,'cc-button--accept')]",
    #         "//button[contains(text(),'Accept')]",
    #         "//button[@id='onetrust-accept-btn-handler']",
    #     )
    #
    #     try:
    #         driver.get("https://link.springer.com/search")
    #         wait = make_wait(driver, timeout=20)
    #
    #         dismiss_cookie_banner(driver, *_COOKIE_XPATHS, timeout=6)
    #
    #         # Submit query via search input
    #         try:
    #             search_box = wait.until(
    #                 EC.element_to_be_clickable((By.NAME, "query"))
    #             )
    #             search_box.clear()
    #             search_box.send_keys(query)
    #             search_box.send_keys(Keys.RETURN)
    #             wait.until(
    #                 EC.presence_of_element_located(
    #                     (By.XPATH, "//li[@data-test='search-result-item']")
    #                 )
    #             )
    #         except TimeoutException:
    #             self._log.warning("Springer Selenium — search submission timed out")
    #             return articles
    #
    #         page = 0
    #         while True:
    #             page += 1
    #             self._log.info("Springer Selenium — scraping page %d", page)
    #
    #             results = driver.find_elements(
    #                 By.XPATH, "//li[@data-test='search-result-item']"
    #             )
    #             for result in results:
    #                 article = _parse_selenium_item(result)
    #                 if article:
    #                     articles.append(article)
    #
    #             # Next page
    #             try:
    #                 next_btn = wait.until(
    #                     EC.element_to_be_clickable(
    #                         (By.XPATH, "//a[@data-test='next-page']")
    #                     )
    #                 )
    #                 next_btn.click()
    #                 time.sleep(3)
    #             except (NoSuchElementException, TimeoutException):
    #                 self._log.info(
    #                     "Springer Selenium — no more pages after page %d", page
    #                 )
    #                 break
    #             except Exception as exc:  # noqa: BLE001
    #                 self._log.warning(
    #                     "Springer Selenium — pagination error: %s", exc
    #                 )
    #                 break
    #
    #     except Exception as exc:  # noqa: BLE001
    #         self._log.error(
    #             "Springer Selenium — fatal error: %s", exc, exc_info=True
    #         )
    #     finally:
    #         driver.quit()
    #
    #     return articles


# ---------------------------------------------------------------------------
# Parsing helpers — API
# ---------------------------------------------------------------------------


def _parse_api_record(rec: dict) -> Article | None:
    """Parse a Springer API record dict into an ``Article``.

    Note: The Springer API occasionally returns list values for fields
    that are normally strings (title, doi, identifier). We coerce these
    defensively to avoid ``'list' object has no attribute 'strip'`` errors.
    """
    try:
        raw_title = rec.get("title") or ""
        # Coerce list → string (Springer sometimes returns a list)
        if isinstance(raw_title, list):
            raw_title = " ".join(str(t) for t in raw_title)
        title = str(raw_title).strip()
        if not title:
            return None

        # DOI: prefer the explicit 'doi' field; fall back to parsing 'identifier'
        raw_doi = rec.get("doi") or ""
        if isinstance(raw_doi, list):
            raw_doi = raw_doi[0] if raw_doi else ""
        doi = str(raw_doi).strip()

        if not doi:
            identifier = rec.get("identifier") or ""  # e.g. "doi:10.1007/s00453-025-01296-3"
            if isinstance(identifier, list):
                identifier = identifier[0] if identifier else ""
            identifier = str(identifier)
            if identifier.lower().startswith("doi:"):
                doi = identifier[4:].strip()

        year = _extract_year_from_date(
            rec.get("publicationDate") or rec.get("onlineDate") or ""
        )
        creators = rec.get("creators") or []
        authors: list[dict[str, str]] = []
        for c in creators:
            # creators is a list of dicts: [{"creator": "Lastname, Firstname"}, ...]
            if not isinstance(c, dict):
                continue
            name = (c.get("creator") or "").strip()
            if name:
                parts = name.split(",", 1)
                authors.append(
                    {
                        "lastName": parts[0].strip(),
                        "fullName": name,
                    }
                )

        # abstract can be: a plain string, a dict {"h1":..., "p": str|list}, or None
        raw_abstract = rec.get("abstract") or ""
        if isinstance(raw_abstract, dict):
            p = raw_abstract.get("p") or ""
            if isinstance(p, list):
                abstract = " ".join(str(x) for x in p).strip()
            else:
                abstract = str(p).strip()
        elif isinstance(raw_abstract, list):
            abstract = " ".join(str(x) for x in raw_abstract).strip()
        else:
            abstract = str(raw_abstract).strip()

        return Article(
            title=title,
            authors=authors,
            publication_year=year,
            doi=doi,
            source=_SOURCE_URL,
            abstract=abstract,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Springer API — parse error: %s", exc)
        return None


def _extract_year_from_date(date_str: str) -> str:
    match = re.search(r"\b(19|20)\d{2}\b", date_str)
    return match.group(0) if match else ""


# ---------------------------------------------------------------------------
# Parsing helpers — Selenium (DISABLED)
# ---------------------------------------------------------------------------
#
# _DOI_HREF_RE = re.compile(r"(10\.\d{4,}/[^\s\"'<>]+)")
#
#
# def _parse_selenium_item(item) -> Article | None:  # type: ignore[no-untyped-def]
#     try:
#         from selenium.webdriver.common.by import By
#
#         # Title
#         title = ""
#         for xpath in (
#             ".//h3[@data-test='title']/a",
#             ".//h3[@data-test='title']",
#             ".//h2",
#         ):
#             try:
#                 title = item.find_element(By.XPATH, xpath).text.strip()
#                 if title:
#                     break
#             except Exception:  # noqa: BLE001
#                 continue
#         if not title:
#             return None
#
#         # Authors
#         authors: list[dict[str, str]] = []
#         try:
#             authors_text = item.find_element(
#                 By.XPATH, ".//span[@data-test='authors']"
#             ).text
#             for name in authors_text.split(","):
#                 name = name.strip()
#                 if name:
#                     authors.append({"lastName": name.split()[-1], "fullName": name})
#         except Exception:  # noqa: BLE001
#             pass
#
#         # Year — from the published span
#         year = ""
#         try:
#             date_text = item.find_element(
#                 By.XPATH, ".//span[@data-test='published']"
#             ).text
#             m = re.search(r"\b(19|20)\d{2}\b", date_text)
#             if m:
#                 year = m.group(0)
#         except Exception:  # noqa: BLE001
#             pass
#
#         # DOI — from href attribute of the article link
#         doi = ""
#         try:
#             href = item.find_element(
#                 By.XPATH, ".//h3[@data-test='title']/a"
#             ).get_attribute("href") or ""
#             m = _DOI_HREF_RE.search(href)
#             if m:
#                 doi = m.group(1)
#         except Exception:  # noqa: BLE001
#             pass
#
#         return Article(
#             title=title,
#             authors=authors,
#             publication_year=year,
#             doi=doi,
#             source=_SOURCE_URL,
#         )
#     except Exception as exc:  # noqa: BLE001
#         logger.warning("Springer Selenium — parse error: %s", exc)
#         return None
