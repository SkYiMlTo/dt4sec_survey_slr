"""
slr/pipeline.py
================
Main orchestration layer for the SLR pipeline.

Execution order
---------------
1. **Extract** — all configured extractors run concurrently in a thread pool.
   Each extractor catches its own exceptions; a failure in one does not
   abort the others.
2. **Merge** — results from all extractors are merged into a single corpus.
3. **Deduplicate** — three-layer dedup (DOI, title-exact, title-fuzzy).
4. **Filter** — articles without a valid DOI are removed.
5. **Export** — combined CSV + styled Excel workbook written to disk.
6. **Visualize** — per-year and per-author charts generated from CSV.

All stage counts are logged for reproducibility / audit.
"""
from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING

from slr.extractors.acm import AcmExtractor
from slr.extractors.computer_org import ComputerOrgExtractor
from slr.extractors.ieee import IeeeExtractor
from slr.extractors.semantic_scholar import SemanticScholarExtractor
from slr.extractors.springer import SpringerExtractor
from slr.exporters.csv_exporter import export_csv
from slr.exporters.excel_exporter import export_excel
from slr.models import Article
from slr.processors.deduplicator import deduplicate
from slr.processors.doi_filter import filter_no_doi
from slr.visualization.authors_chart import generate_authors_chart
from slr.visualization.years_chart import generate_years_chart
from utils.paths import (
    get_dedup_dir,
    get_doi_filtered_dir,
    get_export_dir,
    get_raw_dir,
    get_visualization_dir,
)

if TYPE_CHECKING:
    from slr.extractors.base import BaseExtractor

logger = logging.getLogger(__name__)


def run_pipeline(query: str, run_dir: Path) -> Path:
    """Execute the full SLR pipeline and return the path to the export directory.

    Parameters
    ----------
    query:
        The boolean search string used for all databases.
    run_dir:
        Timestamped output directory created by ``utils.paths.make_run_dir()``.

    Returns
    -------
    Path to the export directory containing the final CSV and Excel files.
    """
    raw_dir = get_raw_dir(run_dir)
    dedup_dir = get_dedup_dir(run_dir)
    doi_dir = get_doi_filtered_dir(run_dir)
    export_dir = get_export_dir(run_dir)
    viz_dir = get_visualization_dir(run_dir)

    logger.info("=" * 60)
    logger.info("SLR PIPELINE START")
    logger.info("Query: %s", query)
    logger.info("Run directory: %s", run_dir)
    logger.info("=" * 60)

    # ── Stage 1: Extraction ─────────────────────────────────────────────────
    logger.info("[Stage 1/5] Extracting from databases …")

    extractors: list[BaseExtractor] = [
        AcmExtractor(output_dir=raw_dir),
        SpringerExtractor(output_dir=raw_dir),
        ComputerOrgExtractor(output_dir=raw_dir),
        IeeeExtractor(output_dir=raw_dir),           # No-op if IEEE_API_KEY unset
        SemanticScholarExtractor(output_dir=raw_dir),
    ]

    corpus: list[Article] = []

    with ThreadPoolExecutor(max_workers=len(extractors), thread_name_prefix="extractor") as pool:
        futures = {
            pool.submit(extractor.extract, query): extractor.name
            for extractor in extractors
        }

        for future in as_completed(futures):
            name = futures[future]
            try:
                results = future.result()
                logger.info("[Stage 1] %-30s -> %d articles", name, len(results))
                corpus.extend(results)
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "[Stage 1] %-30s FAILED: %s", name, exc, exc_info=True
                )

    logger.info("[Stage 1] Total raw articles: %d", len(corpus))

    # ── Stage 2: Deduplication ──────────────────────────────────────────────
    logger.info("[Stage 2/5] Deduplicating …")
    unique_articles, dedup_report = deduplicate(corpus)
    _save_stage_json(unique_articles, dedup_dir / "deduped_articles.json")

    # ── Stage 3: DOI Filter ─────────────────────────────────────────────────
    logger.info("[Stage 3/5] Filtering articles without valid DOIs …")
    final_articles, filter_report = filter_no_doi(unique_articles)
    _save_stage_json(final_articles, doi_dir / "doi_filtered_articles.json")

    # ── Stage 4: Export ─────────────────────────────────────────────────────
    logger.info("[Stage 4/5] Exporting results …")
    csv_path = export_csv(final_articles, export_dir)
    export_excel(final_articles, export_dir)

    # ── Stage 5: Visualize ──────────────────────────────────────────────────
    logger.info("[Stage 5/5] Generating visualizations …")
    generate_years_chart(csv_path, viz_dir)
    generate_authors_chart(csv_path, viz_dir)

    # ── Final summary ────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("SLR PIPELINE COMPLETE")
    logger.info("  Raw articles collected : %d", len(corpus))
    logger.info("  After deduplication    : %d", dedup_report.output_count)
    logger.info("  After DOI filter       : %d", filter_report.output_count)
    logger.info("  Output directory       : %s", export_dir)
    logger.info("=" * 60)

    return export_dir


def _save_stage_json(articles: list[Article], path: Path) -> None:
    """Persist a pipeline stage snapshot as JSON for debugging."""
    data = [a.to_dict() for a in articles]
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.debug("Stage snapshot saved: %s (%d articles)", path.name, len(data))
