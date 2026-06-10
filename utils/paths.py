"""
utils/paths.py
==============
Output path management for the SLR pipeline.

All output is written under ``./output/<timestamp>/``.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_ROOT_OUTPUT: Path = Path("./output")


def make_run_dir(root: Path = _ROOT_OUTPUT) -> Path:
    """Create and return a timestamped run directory.

    The directory name is an ISO-8601 UTC timestamp with colons replaced
    by hyphens so it is safe on all filesystems:
    ``./output/2026-06-03T12-00-00Z/``
    """
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    run_dir = root / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Run directory: %s", run_dir.resolve())
    return run_dir


def get_article_selection_dir(run_dir: Path) -> Path:
    d = run_dir / "articleSelection"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_raw_dir(run_dir: Path) -> Path:
    d = get_article_selection_dir(run_dir) / "step1_raw"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_dedup_dir(run_dir: Path) -> Path:
    d = get_article_selection_dir(run_dir) / "step2_dedup"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_doi_filtered_dir(run_dir: Path) -> Path:
    d = get_article_selection_dir(run_dir) / "step3_doi_filtered"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_export_dir(run_dir: Path) -> Path:
    d = get_article_selection_dir(run_dir) / "step4_export"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_visualization_dir(run_dir: Path) -> Path:
    d = run_dir / "dataVisualization"
    d.mkdir(parents=True, exist_ok=True)
    return d
