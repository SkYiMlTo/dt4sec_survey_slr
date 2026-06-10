"""
config.py
=========
Single source of truth for all pipeline configuration.

Edit this file to change the search query, output directory, rate limits,
or enable/disable specific extractors.

Environment variables (optional — see ``.env.example``)
---------------------------------------------------------
- ``IEEE_API_KEY``              — enables IEEE Xplore API extraction
- ``SPRINGER_API_KEY``          — enables Springer Nature API (faster, more stable)
- ``SEMANTIC_SCHOLAR_API_KEY``  — grants higher Semantic Scholar rate limits
"""
from __future__ import annotations

from pathlib import Path

# ── Search query ────────────────────────────────────────────────────────────
# This is your SLR's boolean query string.  Edit it here — all extractors
# receive this exact string.
SEARCH_QUERY: str = (
    '("Digital Twin" OR "Digital Twins") '
    'AND ("cyberattack" OR "cyberattacks" OR "cyber attack" OR "cyber attacks" '
    'OR "cybersecurity" OR "cyber-security") '
    'AND ("internet of things" OR "IoT" OR "CPS" '
    'OR "cyber-physical systems")'
)

# ── Output directory ─────────────────────────────────────────────────────────
OUTPUT_ROOT: Path = Path("./output")

# ── Rate limiting defaults ────────────────────────────────────────────────────
# These are conservative defaults.  Increase ``REQUESTS_PER_SECOND`` only if
# you have an API key that permits higher throughput.
HTTP_REQUESTS_PER_SECOND: float = 0.5  # 1 req every 2 s (safe default)
HTTP_MAX_RETRIES: int = 5
HTTP_BACKOFF_FACTOR: float = 1.5       # Retry delays: 1.5s, 3s, 6s, 12s, 24s

# ── Deduplication ─────────────────────────────────────────────────────────────
# Minimum rapidfuzz token_sort_ratio score (0–100) to treat two titles as
# duplicates.  95 is a good balance — lower values may merge distinct papers.
FUZZY_DEDUP_THRESHOLD: int = 95

# ── Logging ───────────────────────────────────────────────────────────────────
import logging
LOG_LEVEL: int = logging.INFO
