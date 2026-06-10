"""
slr/processors/deduplicator.py
================================
Three-layer deduplication for the merged article corpus.

Deduplication layers (applied in order, first match wins)
----------------------------------------------------------
1. **Exact DOI** — two articles with identical normalised DOIs are
   definitive duplicates regardless of title differences.
2. **Normalised title exact** — after stripping punctuation, collapsing
   whitespace, lowercasing, and removing leading articles ("a", "an", "the"),
   identical strings are treated as duplicates.
3. **Fuzzy title similarity** — uses ``rapidfuzz.fuzz.token_sort_ratio``
   with a configurable threshold (default 95 %).  This catches cases like
   "A Survey of Digital Twin Cybersecurity" vs.
   "Survey of Digital Twin Cyber-security".

Audit trail
-----------
``deduplicate()`` returns both the cleaned list and a ``DeduplicationReport``
with per-source counts and details of every merge decision for reproducibility.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final

from slr.models import Article, normalise_title

logger = logging.getLogger(__name__)

try:
    from rapidfuzz import fuzz as _fuzz  # type: ignore[import-untyped]
    _RAPIDFUZZ_AVAILABLE = True
except ModuleNotFoundError:
    _RAPIDFUZZ_AVAILABLE = False
    logger.warning(
        "rapidfuzz not installed — fuzzy deduplication disabled. "
        "Install it with: pip install rapidfuzz"
    )

# Minimum fuzzy similarity score (0–100) to consider two titles duplicates
DEFAULT_FUZZY_THRESHOLD: Final[int] = 95


@dataclass
class DeduplicationReport:
    """Summary statistics and merge log from a deduplication run."""

    input_count: int = 0
    output_count: int = 0
    doi_duplicates: int = 0
    title_exact_duplicates: int = 0
    title_fuzzy_duplicates: int = 0

    # Details: list of (kept_title, dropped_title, reason)
    merge_log: list[tuple[str, str, str]] = field(default_factory=list)

    @property
    def total_dropped(self) -> int:
        return self.input_count - self.output_count

    def summary(self) -> str:
        return (
            f"Deduplication: {self.input_count} in -> {self.output_count} out "
            f"({self.total_dropped} dropped: "
            f"{self.doi_duplicates} DOI-exact, "
            f"{self.title_exact_duplicates} title-exact, "
            f"{self.title_fuzzy_duplicates} title-fuzzy)"
        )


def deduplicate(
    articles: list[Article],
    fuzzy_threshold: int = DEFAULT_FUZZY_THRESHOLD,
) -> tuple[list[Article], DeduplicationReport]:
    """Remove duplicate articles using a three-layer strategy.

    Parameters
    ----------
    articles:
        The merged corpus from all extractors.
    fuzzy_threshold:
        Minimum ``token_sort_ratio`` score (0–100) for fuzzy title matching.
        Higher = stricter (fewer merges).

    Returns
    -------
    (unique_articles, report)
        A list of deduplicated ``Article`` objects and a
        ``DeduplicationReport`` with audit details.
    """
    report = DeduplicationReport(input_count=len(articles))

    seen_dois: dict[str, str] = {}         # normalised_doi → kept title
    seen_norm_titles: dict[str, str] = {}  # normalised_title → kept title
    seen_norm_title_list: list[str] = []   # ordered for fuzzy scan

    unique: list[Article] = []

    for article in articles:
        norm_doi = article._normalised_doi
        norm_title = article._normalised_title

        # ── Layer 1: DOI exact match ────────────────────────────────────────
        if norm_doi and norm_doi in seen_dois:
            kept = seen_dois[norm_doi]
            report.doi_duplicates += 1
            report.merge_log.append((kept, article.title, "DOI-exact"))
            logger.debug(
                "DOI-dup dropped: %r (kept: %r)", article.title[:60], kept[:60]
            )
            continue

        # ── Layer 2: Normalised title exact match ───────────────────────────
        if norm_title and norm_title in seen_norm_titles:
            kept = seen_norm_titles[norm_title]
            report.title_exact_duplicates += 1
            report.merge_log.append((kept, article.title, "title-exact"))
            logger.debug(
                "Title-exact-dup dropped: %r", article.title[:60]
            )
            continue

        # ── Layer 3: Fuzzy title match ──────────────────────────────────────
        if norm_title and _RAPIDFUZZ_AVAILABLE:
            fuzzy_match = _find_fuzzy_match(
                norm_title, seen_norm_title_list, fuzzy_threshold
            )
            if fuzzy_match is not None:
                kept = seen_norm_titles.get(fuzzy_match, fuzzy_match)
                report.title_fuzzy_duplicates += 1
                report.merge_log.append(
                    (kept, article.title, f"title-fuzzy≥{fuzzy_threshold}")
                )
                logger.debug(
                    "Fuzzy-dup dropped: %r (similar to: %r)",
                    article.title[:60], kept[:60],
                )
                continue

        # ── Not a duplicate — record and keep ──────────────────────────────
        if norm_doi:
            seen_dois[norm_doi] = article.title
        if norm_title:
            seen_norm_titles[norm_title] = article.title
            seen_norm_title_list.append(norm_title)

        unique.append(article)

    report.output_count = len(unique)
    logger.info(report.summary())
    return unique, report


def _find_fuzzy_match(
    candidate: str,
    corpus: list[str],
    threshold: int,
) -> str | None:
    """Return the first corpus entry that matches *candidate* above *threshold*.

    Uses ``token_sort_ratio`` which is invariant to word order, making it
    robust to minor reorderings in academic titles.

    Returns ``None`` if no match found.
    """
    if not _RAPIDFUZZ_AVAILABLE or not corpus:
        return None

    for existing in corpus:
        score = _fuzz.token_sort_ratio(candidate, existing)
        if score >= threshold:
            return existing
    return None
