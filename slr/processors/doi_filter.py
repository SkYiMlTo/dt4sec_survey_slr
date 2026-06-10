"""
slr/processors/doi_filter.py
=============================
DOI validation and filtering stage.

Filters out articles whose DOI field:
- Is absent or blank
- Is a known sentinel value ("N/A", "null", "none", …)
- Is only the doi.org URL prefix with no actual identifier
- Fails to match the standard DOI regex (^10.XXXX/... format)

All filtered articles are logged with a reason for the audit trail.

Why this matters
----------------
``"https://doi.org/"`` (just the prefix, no path) which slipped through
the old filter's simple truthiness check.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from slr.models import Article, is_valid_doi

logger = logging.getLogger(__name__)

# DOI must start with "10." followed by 4+ digits, slash, then at least one
# non-whitespace character.
_DOI_PATTERN = re.compile(r"^10[.]\d{4,}/\S+$", re.IGNORECASE)

# Sentinel strings that the old extractors sometimes emitted
_REJECT_SENTINELS: frozenset[str] = frozenset(
    {
        "",
        "n/a",
        "n.a.",
        "none",
        "null",
        "na",
        "https://doi.org/",
        "http://doi.org/",
        "doi:",
        "doi",
    }
)


@dataclass
class FilterReport:
    """Summary of the DOI filtering stage."""

    input_count: int = 0
    output_count: int = 0
    # reason → count
    rejection_reasons: dict[str, int] = field(default_factory=dict)

    @property
    def rejected_count(self) -> int:
        return self.input_count - self.output_count

    def summary(self) -> str:
        reasons = ", ".join(
            f"{r}: {n}" for r, n in sorted(self.rejection_reasons.items())
        )
        return (
            f"DOI filter: {self.input_count} in -> {self.output_count} out "
            f"({self.rejected_count} rejected: {reasons or 'none'})"
        )


def filter_no_doi(articles: list[Article]) -> tuple[list[Article], FilterReport]:
    """Remove articles without a valid DOI.

    Parameters
    ----------
    articles:
        Input corpus (post-deduplication).

    Returns
    -------
    (valid_articles, report)
    """
    report = FilterReport(input_count=len(articles))
    valid: list[Article] = []

    for article in articles:
        reason = _rejection_reason(article.doi)
        if reason:
            report.rejection_reasons[reason] = (
                report.rejection_reasons.get(reason, 0) + 1
            )
            logger.debug(
                "Filtered out %r — DOI=%r (%s)",
                article.title[:60],
                article.doi,
                reason,
            )
        else:
            valid.append(article)

    report.output_count = len(valid)
    logger.info(report.summary())
    return valid, report


def _rejection_reason(doi: str) -> str | None:
    """Return a human-readable rejection reason, or ``None`` if valid."""
    if not doi:
        return "missing"

    normalised = doi.strip().lower()

    if normalised in _REJECT_SENTINELS:
        return f"sentinel({doi!r})"

    if not _DOI_PATTERN.match(doi.strip()):
        return "invalid-format"

    return None  # DOI is valid
