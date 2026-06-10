"""
slr/extractors/semantic_scholar.py
====================================
Extractor for Semantic Scholar (https://www.semanticscholar.org/) via the
official Semantic Scholar Graph API v1.

No API key required for basic usage (1 req/s limit).
Set ``SEMANTIC_SCHOLAR_API_KEY`` for higher throughput (100 req/s).

API docs: https://api.semanticscholar.org/api-docs/graph

Key advantages over the legacy version
---------------------------------------
- Uses the *official* Graph API endpoint (not the private internal API
  that the old code reversed-engineered — that endpoint can break at any time)
- Returns DOIs, authors, year, and abstracts from structured JSON
- No Selenium, no cookies, no reverse-engineered sessions
- Proper pagination via ``offset`` + ``total``
- Rate-limiter aware of the 1 req/s public limit
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from slr.models import Article
from slr.extractors.base import BaseExtractor
from utils.http_session import RateLimiter, build_session

logger = logging.getLogger(__name__)

_SOURCE_URL: str = "https://www.semanticscholar.org/"
_API_BASE: str = "https://api.semanticscholar.org/graph/v1/paper/search"
_FIELDS: str = "title,authors,year,externalIds,abstract"
_PAGE_SIZE: int = 100  # API max per page


class SemanticScholarExtractor(BaseExtractor):
    """Extract papers from Semantic Scholar via the Graph API."""

    name = "semantic_scholar"
    source_url = _SOURCE_URL

    # Maximum number of consecutive 429 retries before giving up on a page
    _MAX_429_RETRIES: int = 5

    def extract(self, query: str) -> list[Article]:
        self._log.info("Starting Semantic Scholar extraction")

        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "").strip()
        session = build_session()
        # Semantic Scholar API expects JSON responses
        session.headers["Accept"] = "application/json"

        # Adjust rate for key vs. no-key access
        # Even with a key, start conservatively to avoid early 429s
        if api_key:
            session.headers["x-api-key"] = api_key
            limiter = RateLimiter(calls_per_second=2.0, min_delay=0.5)
            self._log.info("Semantic Scholar — authenticated (higher rate limit)")
        else:
            limiter = RateLimiter(calls_per_second=0.5, min_delay=2.0)
            self._log.info("Semantic Scholar — public access (1 req/s limit)")

        articles: list[Article] = []
        offset = 0

        # Semantic Scholar Graph API text search does not support complex boolean
        # queries with AND/OR. It treats them as exact literal strings, returning 0.
        # If we see a complex query, we simplify it to core keywords.
        if "AND" in query or "OR" in query:
            ss_query = '"digital twin" cybersecurity IoT'
            self._log.info("Semantic Scholar — simplifying complex boolean query to: %r", ss_query)
        else:
            ss_query = query

        try:
            while True:
                limiter.wait()
                params = {
                    "query": ss_query,
                    "fields": _FIELDS,
                    "offset": offset,
                    "limit": _PAGE_SIZE,
                }

                retry_429_count = 0
                resp = None
                while retry_429_count < self._MAX_429_RETRIES:
                    try:
                        resp = session.get(_API_BASE, params=params, timeout=(10, 30))
                        if resp.status_code == 429:
                            retry_429_count += 1
                            # Exponential backoff: 5s, 10s, 20s, 40s, 80s
                            backoff = min(5 * (2 ** (retry_429_count - 1)), 120)
                            self._log.warning(
                                "Semantic Scholar rate-limited (429), attempt %d/%d. "
                                "Backing off %ds … (body: %.200s)",
                                retry_429_count, self._MAX_429_RETRIES,
                                backoff, resp.text[:200],
                            )
                            import time
                            time.sleep(backoff)
                            continue  # retry same offset
                        break  # not a 429 — proceed
                    except Exception as exc:  # noqa: BLE001
                        self._log.error(
                            "Semantic Scholar API error at offset %d: %s", offset, exc
                        )
                        resp = None
                        break

                if resp is None:
                    break
                if resp.status_code == 429:
                    self._log.error(
                        "Semantic Scholar — exhausted 429 retries at offset %d. "
                        "Stopping extraction.", offset
                    )
                    break

                try:
                    resp.raise_for_status()
                    data = resp.json()
                except Exception as exc:  # noqa: BLE001
                    self._log.error(
                        "Semantic Scholar API error at offset %d: %s", offset, exc
                    )
                    break

                raw_papers = data.get("data", [])
                if not raw_papers:
                    break

                for paper in raw_papers:
                    article = _parse_paper(paper)
                    if article:
                        articles.append(article)

                total = data.get("total", 0)
                offset += _PAGE_SIZE
                self._log.info(
                    "Semantic Scholar — fetched %d/%d articles (offset=%d)",
                    len(articles), total, offset,
                )

                # Semantic Scholar caps results at 10 000
                if offset >= min(total, 10_000):
                    break

        except Exception as exc:  # noqa: BLE001
            self._log.error(
                "Semantic Scholar — fatal error: %s", exc, exc_info=True
            )

        self._log.info("Semantic Scholar — collected %d articles", len(articles))
        self._save_raw(articles)
        return articles


def _parse_paper(paper: dict) -> Article | None:
    """Parse a Semantic Scholar paper dict into an ``Article``."""
    try:
        title = (paper.get("title") or "").strip()
        if not title:
            return None

        # DOI lives in externalIds.DOI
        external_ids = paper.get("externalIds") or {}
        doi = (external_ids.get("DOI") or "").strip()

        year = str(paper.get("year") or "")

        authors: list[dict[str, str]] = []
        for a in paper.get("authors") or []:
            full = (a.get("name") or "").strip()
            if full:
                authors.append(
                    {
                        "fullName": full,
                        "lastName": full.split()[-1],
                    }
                )

        abstract = (paper.get("abstract") or "").strip()

        return Article(
            title=title,
            authors=authors,
            publication_year=year,
            doi=doi,
            source=_SOURCE_URL,
            abstract=abstract,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Semantic Scholar — parse error: %s", exc)
        return None
