"""
slr/extractors/ieee.py
======================
Extractor for IEEE Xplore (https://ieeexplore.ieee.org/) via the official
IEEE Xplore REST API.

Requires the ``IEEE_API_KEY`` environment variable.  When the variable is
absent this extractor logs a warning and returns an empty list — it does
NOT fall back to cookie-based scraping (those cookies expire in hours and
are tied to individual institutional sessions).

API reference: https://developer.ieee.org/
Free tier: 200 req/day, up to 200 records/call.

Key advantages over the legacy version
---------------------------------------
- No Selenium, no browser — pure HTTP REST calls
- DOIs, titles, authors, and years come from structured JSON — no parsing
- Exponential back-off and rate limiting built in via ``build_session``
"""
from __future__ import annotations

import logging
import os
from math import ceil
from pathlib import Path

from slr.models import Article
from slr.extractors.base import BaseExtractor
from utils.http_session import RateLimiter, build_session

logger = logging.getLogger(__name__)

_SOURCE_URL: str = "https://ieeexplore.ieee.org/"
_API_BASE: str = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
_ROWS_PER_PAGE: int = 200  # API max


class IeeeExtractor(BaseExtractor):
    """Extract papers from IEEE Xplore via the official REST API.

    Set ``IEEE_API_KEY`` in the environment (or ``secrets.IEEE_API_KEY``
    in GitHub Actions) to enable this extractor.
    """

    name = "ieee_xplore"
    source_url = _SOURCE_URL

    def extract(self, query: str) -> list[Article]:
        api_key = os.getenv("IEEE_API_KEY", "").strip()
        if not api_key:
            self._log.warning(
                "IEEE Xplore extractor disabled: IEEE_API_KEY not set. "
                "Obtain a free key at https://developer.ieee.org/"
            )
            return []

        self._log.info("Starting IEEE Xplore extraction (API)")
        session = build_session()
        limiter = RateLimiter(calls_per_second=1.0, min_delay=1.0)
        articles: list[Article] = []

        try:
            # First call to discover total record count
            first_batch = self._call_api(session, api_key, query, start_record=1)
            if first_batch is None:
                return articles

            total = first_batch.get("total_records", 0)
            articles.extend(_parse_ieee_records(first_batch.get("articles", [])))

            num_pages = ceil(total / _ROWS_PER_PAGE)
            self._log.info(
                "IEEE Xplore — %d total records across %d pages", total, num_pages
            )

            for page in range(2, num_pages + 1):
                limiter.wait()
                start = (page - 1) * _ROWS_PER_PAGE + 1
                batch = self._call_api(session, api_key, query, start_record=start)
                if batch is None:
                    self._log.warning(
                        "IEEE Xplore — failed to fetch page %d; stopping", page
                    )
                    break
                articles.extend(_parse_ieee_records(batch.get("articles", [])))
                self._log.debug(
                    "IEEE Xplore — page %d/%d fetched (%d total so far)",
                    page, num_pages, len(articles),
                )

        except Exception as exc:  # noqa: BLE001
            self._log.error("IEEE Xplore — fatal error: %s", exc, exc_info=True)

        self._log.info("IEEE Xplore — collected %d articles", len(articles))
        self._save_raw(articles)
        return articles

    def _call_api(
        self,
        session,
        api_key: str,
        query: str,
        start_record: int = 1,
    ) -> dict | None:
        params = {
            "apikey": api_key,
            "querytext": query,
            "start_record": start_record,
            "max_records": _ROWS_PER_PAGE,
            "format": "json",
        }
        try:
            resp = session.get(_API_BASE, params=params, timeout=(10, 30))
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # noqa: BLE001
            self._log.error(
                "IEEE Xplore API call failed (start=%d): %s", start_record, exc
            )
            return None


def _parse_ieee_records(records: list[dict]) -> list[Article]:
    articles: list[Article] = []
    for rec in records:
        try:
            title = (rec.get("title") or "").strip()
            if not title:
                continue

            doi = rec.get("doi") or ""
            year = str(rec.get("publication_year") or "")

            authors: list[dict[str, str]] = []
            for a in rec.get("authors", {}).get("authors", []):
                full = (a.get("full_name") or "").strip()
                if full:
                    authors.append(
                        {
                            "lastName": full.split()[-1],
                            "fullName": full,
                        }
                    )

            abstract = (rec.get("abstract") or "").strip()

            articles.append(
                Article(
                    title=title,
                    authors=authors,
                    publication_year=year,
                    doi=doi,
                    source=_SOURCE_URL,
                    abstract=abstract,
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("IEEE Xplore — parse error: %s", exc)

    return articles
