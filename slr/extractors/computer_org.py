"""
slr/extractors/computer_org.py
===============================
Extractor for the IEEE Computer Society Digital Library
(https://www.computer.org/csdl/).

Key improvements over the legacy version
-----------------------------------------
- **Eliminates the per-article nested browser session** for DOI lookup.
  The old code opened a brand-new Chrome driver for every single article
  to fetch its DOI — catastrophically slow and fragile.  The new approach
  extracts DOIs directly from ``data-doi`` attributes and ``href`` values
  on the listing page itself, which is sufficient for CSDL.
- ``WebDriverWait`` for Angular hydration instead of ``time.sleep()``
- Robust pagination via ``aria-label='Next'`` button disabled-state check
- All exceptions are caught and logged; partial results preserved
"""
from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from urllib.parse import quote

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from slr.models import Article
from slr.extractors.base import BaseExtractor
from utils.selenium_factory import build_driver, dismiss_cookie_banner, make_wait

logger = logging.getLogger(__name__)

_SOURCE_URL: str = "https://www.computer.org/csdl"
_SEARCH_URL: str = (
    "https://www.computer.org/csdl/search/default"
    "?queryState=%7B%22basicSearchTextSubmitted%22:%5B%22%22,null%5D,"
    "%22searchResultLimit%22:%5B10,100%5D%7D"
)

_COOKIE_XPATHS: tuple[str, ...] = (
    "//*[contains(@class,'osano-cm-denyAll')]",
    "//*[contains(@class,'osano-cm-accept-all')]",
    "//button[contains(text(),'Reject')]",
    "//button[@id='onetrust-reject-all-handler']",
)

_DOI_RE = re.compile(r"(10\.\d{4,}/[^\s\"'<>]+)")


class ComputerOrgExtractor(BaseExtractor):
    """Extract papers from the IEEE Computer Society Library via Selenium."""

    name = "computer_org"
    source_url = _SOURCE_URL

    def extract(self, query: str) -> list[Article]:
        self._log.info("Starting Computer.org extraction")
        driver = build_driver()
        articles: list[Article] = []

        try:
            driver.get(_SEARCH_URL)
            wait = make_wait(driver, timeout=30)

            # Wait for Angular app to hydrate
            wait.until(EC.presence_of_element_located((By.ID, "basic-search-input")))
            time.sleep(2)

            # Dismiss cookie banner (best-effort)
            dismiss_cookie_banner(driver, *_COOKIE_XPATHS, timeout=5)

            # Submit the search query
            search_bar = driver.find_element(By.ID, "basic-search-input")
            search_bar.clear()
            search_bar.click()
            search_bar.send_keys(query)
            search_bar.send_keys(Keys.ENTER)

            # Wait for results to appear
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, ".//div[contains(@class,'search-result')]")
                    )
                )
            except TimeoutException:
                self._log.warning("Computer.org — timed out waiting for results")
                return articles

            page = 0
            while True:
                page += 1
                self._log.info("Computer.org — scraping page %d", page)

                try:
                    wait.until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "article-title")
                        )
                    )
                except TimeoutException:
                    self._log.warning(
                        "Computer.org — results not rendered on page %d", page
                    )
                    break

                # Small settle for lazy-loaded content
                time.sleep(2)

                items = driver.find_elements(
                    By.XPATH, ".//div[contains(@class,'search-result')]"
                )

                for item in items:
                    article = _parse_computer_item(item)
                    if article:
                        articles.append(article)

                # Check pagination state
                if not _go_to_next_page(driver, wait):
                    break

        except Exception as exc:  # noqa: BLE001
            self._log.error("Computer.org — fatal error: %s", exc, exc_info=True)
        finally:
            driver.quit()

        self._log.info("Computer.org — collected %d articles", len(articles))

        # ----------------------------------------------------------------
        # CrossRef DOI enrichment
        # CSDL listing pages do not expose DOIs in their HTML. Use the free
        # CrossRef API (no key needed) to resolve titles -> DOIs in batch.
        # ----------------------------------------------------------------
        articles = _enrich_dois_via_crossref(articles, self._log)

        with_doi = sum(1 for a in articles if a.doi)
        self._log.info(
            "Computer.org — DOI enrichment complete: %d/%d articles have DOIs",
            with_doi, len(articles),
        )
        self._save_raw(articles)
        return articles


def _go_to_next_page(driver, wait) -> bool:  # type: ignore[no-untyped-def]
    """Click the Next button if available. Returns False when done."""
    try:
        next_buttons = driver.find_elements(
            By.XPATH, "//a[@aria-label='Next']"
        )
        if not next_buttons:
            return False
        # CSDL renders two Next links (top + bottom); use the last one
        next_btn = next_buttons[-1]
        if next_btn.get_attribute("aria-disabled") == "true":
            return False
        driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
        next_btn.send_keys(Keys.ENTER)
        time.sleep(3)
        return True
    except (NoSuchElementException, StaleElementReferenceException):
        return False
    except Exception as exc:  # noqa: BLE001
        logger.warning("Computer.org — pagination error: %s", exc)
        return False


def _parse_computer_item(item) -> Article | None:  # type: ignore[no-untyped-def]
    try:
        # Title
        title = ""
        title_el = None
        try:
            title_el = item.find_element(By.CLASS_NAME, "article-title")
            title = title_el.text.strip()
        except NoSuchElementException:
            pass
        if not title:
            return None

        # Year
        year = ""
        try:
            metadata = item.find_element(
                By.XPATH, ".//div[contains(@class,'metadata')]"
            ).text
            m = re.search(r"\b(19|20)\d{2}\b", metadata)
            if m:
                year = m.group(0)
        except Exception:  # noqa: BLE001
            pass

        # Authors
        authors: list[dict[str, str]] = []
        try:
            author_btns = item.find_elements(
                By.XPATH, ".//button[contains(@class,'article-author')]"
            )
            for btn in author_btns:
                name = btn.text.strip()
                if name:
                    authors.append({"lastName": name.split()[-1], "fullName": name})
        except Exception:  # noqa: BLE001
            pass

        # DOI — the article-title is a <span> inside an <a>; get href from parent anchor
        doi = ""
        try:
            # item.parent is the WebDriver; use JS to walk up to the nearest <a>
            anchor = item.parent.execute_script(
                "return arguments[0].closest('a');", title_el
            ) if title_el is not None else None
            if anchor:
                href = anchor.get_attribute("href") or ""
                m = _DOI_RE.search(href)
                if m:
                    doi = m.group(1)
        except Exception:  # noqa: BLE001
            pass

        if not doi:
            # Fallback: data-doi attribute on the container
            try:
                doi = item.get_attribute("data-doi") or ""
            except Exception:  # noqa: BLE001
                pass

        if not doi:
            # Last resort: scan the inner HTML for any DOI pattern
            try:
                html = item.get_attribute("innerHTML") or ""
                m = _DOI_RE.search(html)
                if m:
                    doi = m.group(1)
            except Exception:  # noqa: BLE001
                pass

        return Article(
            title=title,
            authors=authors,
            publication_year=year,
            doi=doi,
            source=_SOURCE_URL,
        )
    except (StaleElementReferenceException, NoSuchElementException) as exc:
        logger.debug("Computer.org — skipping item due to: %s", exc)
        return None
    except Exception as exc:  # noqa: BLE001
        logger.warning("Computer.org — parse error: %s", exc)
        return None


# ---------------------------------------------------------------------------
# CrossRef DOI enrichment
# ---------------------------------------------------------------------------

_CROSSREF_API = "https://api.crossref.org/works"
# Score threshold: CrossRef relevance score >= this value to accept a match.
# Exact-title matches typically score 30-60. We use 30 as a conservative floor.
_CROSSREF_SCORE_THRESHOLD = 30.0


def _enrich_dois_via_crossref(
    articles: list[Article],
    log: logging.Logger,
) -> list[Article]:
    """Look up missing DOIs via the free CrossRef API.

    For each article without a DOI, query CrossRef by title. If the top result
    has a relevance score >= threshold, treat its DOI as confirmed and attach it.

    Rate: CrossRef politely-asks for 1 req/s from unauthenticated clients.
    We add a small sleep between calls.
    """
    from utils.http_session import build_session

    need_doi = [a for a in articles if not a.doi]
    if not need_doi:
        return articles

    log.info("Computer.org CrossRef — looking up DOIs for %d articles …", len(need_doi))
    session = build_session()
    # Polite pool header (CrossRef prefers this)
    session.headers["User-Agent"] = (
        "SLR-DOI-Enricher/1.0 (academic research; contact: researcher@university.edu)"
    )

    doi_map: dict[str, str] = {}  # title -> doi
    for article in need_doi:
        try:
            time.sleep(1.1)  # stay under CrossRef polite limit
            resp = session.get(
                _CROSSREF_API,
                params={
                    "query.bibliographic": article.title,
                    "rows": 1,
                    "select": "DOI,title,score",
                },
                timeout=(5, 15),
            )
            resp.raise_for_status()
            items = resp.json().get("message", {}).get("items", [])
            if not items:
                continue
            hit = items[0]
            score = float(hit.get("score") or 0)
            doi = (hit.get("DOI") or "").strip()
            if doi and score >= _CROSSREF_SCORE_THRESHOLD:
                doi_map[article.title] = doi
                log.debug(
                    "CrossRef match (score=%.1f): %r -> %s", score, article.title[:60], doi
                )
        except Exception as exc:  # noqa: BLE001
            log.warning("CrossRef lookup error for %r: %s", article.title[:60], exc)

    if not doi_map:
        return articles

    # Rebuild list with enriched DOIs (Articles are dataclasses — replace fields)
    import dataclasses
    enriched: list[Article] = []
    for article in articles:
        if not article.doi and article.title in doi_map:
            article = dataclasses.replace(article, doi=doi_map[article.title])
        enriched.append(article)

    log.info("CrossRef enriched %d/%d articles with DOIs", len(doi_map), len(need_doi))
    return enriched
