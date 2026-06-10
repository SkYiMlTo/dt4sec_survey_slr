"""
slr/models.py
=============
Core data model for the SLR pipeline.

All extractors must return ``list[Article]``.  The dataclass normalises
fields on construction so downstream processors can rely on consistent
formatting without defensive coding.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# DOI helpers
# ---------------------------------------------------------------------------

_DOI_RE = re.compile(r"(10\.\d{4,}(?:\.\d+)*/[^\s\"'<>]+)", re.IGNORECASE)
_DOI_URL_PREFIX = "https://doi.org/"

# Sentinel values that should be treated as "no DOI"
_EMPTY_SENTINELS: frozenset[str] = frozenset(
    {"", "n/a", "n.a.", "none", "null", "na", _DOI_URL_PREFIX}
)


def normalise_doi(raw: str | None) -> str:
    """Extract and normalise a DOI string.

    Returns an empty string when no valid DOI can be found.

    Examples
    --------
    >>> normalise_doi("https://doi.org/10.1109/ACCESS.2022.123456")
    '10.1109/access.2022.123456'
    >>> normalise_doi("DOI: 10.1234/example")
    '10.1234/example'
    >>> normalise_doi("N/A")
    ''
    """
    if not raw:
        return ""

    # Strip whitespace and common decorators
    raw = raw.strip().rstrip(".")

    # Already a bare DOI?
    match = _DOI_RE.search(raw)
    if match:
        return match.group(1).lower()

    # Could be the href form: "href=\"/10.1234/...\""
    cleaned = raw.replace("href=", "").replace('"', "").strip("/")
    match = _DOI_RE.search(cleaned)
    if match:
        return match.group(1).lower().rstrip('"\'')

    return ""


def is_valid_doi(doi: str) -> bool:
    """Return True if *doi* is a properly formatted DOI string."""
    if not doi:
        return False
    normalised = doi.strip().lower()
    if normalised in _EMPTY_SENTINELS:
        return False
    return bool(_DOI_RE.fullmatch(doi.strip()))


# ---------------------------------------------------------------------------
# Title helpers
# ---------------------------------------------------------------------------

_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_LEADING_ARTICLES = frozenset({"a", "an", "the"})


def normalise_title(raw: str) -> str:
    """Return a canonical form of *raw* suitable for deduplication.

    Steps:
    1. Unicode NFKC normalisation (e.g., ligatures → plain ASCII)
    2. Lowercase
    3. Strip punctuation
    4. Collapse whitespace
    5. Strip leading articles (a / an / the)
    """
    if not raw:
        return ""
    text = unicodedata.normalize("NFKC", raw).lower()
    text = _PUNCT_RE.sub(" ", text)
    tokens = text.split()
    if tokens and tokens[0] in _LEADING_ARTICLES:
        tokens = tokens[1:]
    return " ".join(tokens)


# ---------------------------------------------------------------------------
# Author helpers
# ---------------------------------------------------------------------------


def format_authors(authors: list[dict[str, str]]) -> str:
    """Flatten a list of author dicts to a comma-separated string."""
    names: list[str] = []
    for a in authors:
        # Support {'lastName': ...}, {'name': ...}, or {'fullName': ...}
        name = (
            a.get("fullName")
            or a.get("name")
            or a.get("lastName")
            or ""
        ).strip()
        if name:
            names.append(name)
    return ", ".join(names) if names else "No authors"


# ---------------------------------------------------------------------------
# Article dataclass
# ---------------------------------------------------------------------------


@dataclass
class Article:
    """Represents a single academic paper retrieved by any extractor.

    All fields are normalised on construction via ``__post_init__``.
    """

    title: str
    authors: list[dict[str, str]]
    publication_year: str
    doi: str
    source: str
    abstract: str = ""

    # Computed / derived — not part of constructor equality
    _normalised_title: str = field(default="", init=False, repr=False, compare=False)
    _normalised_doi: str = field(default="", init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        # Normalise all string fields
        self.title = (self.title or "").strip()
        self.publication_year = str(self.publication_year or "").strip()
        self.doi = normalise_doi(self.doi)
        self.source = (self.source or "").strip()
        self.abstract = (self.abstract or "").strip()

        # Ensure authors is always a list
        if not isinstance(self.authors, list):
            self.authors = []

        # Pre-compute derived fields
        self._normalised_title = normalise_title(self.title)
        self._normalised_doi = self.doi

    @property
    def authors_str(self) -> str:
        """Human-readable author list."""
        return format_authors(self.authors)

    @property
    def has_valid_doi(self) -> bool:
        """True if this article carries a properly formatted DOI."""
        return is_valid_doi(self._normalised_doi)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a flat dict suitable for CSV / JSON export."""
        return {
            "title": self.title,
            "authors": self.authors_str,
            "publication_year": self.publication_year,
            "doi": self.doi,
            "source": self.source,
            "abstract": self.abstract,
        }

    def __repr__(self) -> str:
        return (
            f"Article(title={self.title[:60]!r}, "
            f"year={self.publication_year!r}, "
            f"doi={self.doi!r}, "
            f"source={self.source!r})"
        )
