"""
run.py
======
Entry point for the SLR pipeline.

Usage
-----
    # Full run:
    python run.py

    # Dry-run (mocked extractors, validates pipeline without hitting live sites):
    python run.py --dry-run

    # Custom output directory:
    python run.py --output-dir /path/to/output
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SLR Pipeline — Academic database scraper for Systematic Literature Reviews"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline with mock extractors (no live network requests)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override the output root directory (default: ./output)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity (default: INFO)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    import logging

    import config
    from utils.logging_config import setup_logging
    from utils.paths import make_run_dir

    try:
        import dotenv
        dotenv.load_dotenv()
    except ImportError:
        pass

    log_level = getattr(logging, args.log_level, logging.INFO)

    # Create run directory first so logs can be written there
    output_root = args.output_dir or config.OUTPUT_ROOT
    run_dir = make_run_dir(root=output_root)

    setup_logging(run_dir=run_dir, level=log_level)
    logger = logging.getLogger(__name__)

    if args.dry_run:
        logger.info("DRY-RUN mode — using mock extractors")
        _run_dry(run_dir, config.SEARCH_QUERY)
    else:
        from slr.pipeline import run_pipeline
        run_pipeline(query=config.SEARCH_QUERY, run_dir=run_dir)


def _run_dry(run_dir: Path, query: str) -> None:
    """Execute the pipeline with a handful of synthetic articles.

    This validates the full processing chain (dedup, DOI filter, export,
    charts) without making any HTTP or Selenium requests.
    """
    import logging

    from slr.models import Article
    from slr.processors.deduplicator import deduplicate
    from slr.processors.doi_filter import filter_no_doi
    from slr.exporters.csv_exporter import export_csv
    from slr.exporters.excel_exporter import export_excel
    from slr.visualization.years_chart import generate_years_chart
    from slr.visualization.authors_chart import generate_authors_chart
    from utils.paths import (
        get_dedup_dir, get_doi_filtered_dir, get_export_dir, get_visualization_dir
    )

    logger = logging.getLogger(__name__)
    logger.info("Dry-run: building synthetic corpus …")

    mock_articles: list[Article] = [
        Article("Digital Twin Security: A Survey", [{"fullName": "Alice Smith"}], "2022",
                "10.1109/access.2022.001", "https://ieeexplore.ieee.org/"),
        Article("digital twin security a survey", [{"fullName": "Alice Smith"}], "2022",
                "10.1109/ACCESS.2022.001", "https://ieeexplore.ieee.org/"),  # DOI-dup
        Article("Cyber-Physical Systems and Digital Twins", [{"fullName": "Bob Jones"}], "2021",
                "10.1145/3456789", "https://dl.acm.org/"),
        Article("IoT Security with Digital Twin Models", [{"fullName": "Carol Lee"}, {"fullName": "Dave Kim"}], "2023",
                "10.1007/978-3-030-12345-6", "https://link.springer.com/"),
        Article("No DOI Article", [{"fullName": "Eve Brown"}], "2020",
                "", "https://www.computer.org/csdl"),
        Article("Twin Digital Security IoT", [{"fullName": "Frank Wu"}], "2022",
                "N/A", "https://www.semanticscholar.org/"),  # sentinel DOI
        Article("A Study on CPS Vulnerability Detection", [{"fullName": "Grace Chen"}], "2023",
                "10.1016/j.iot.2023.100891", "https://link.springer.com/"),
    ]

    unique, dedup_report = deduplicate(mock_articles)
    final, filter_report = filter_no_doi(unique)

    export_dir = get_export_dir(run_dir)
    viz_dir = get_visualization_dir(run_dir)

    csv_path = export_csv(final, export_dir)
    export_excel(final, export_dir)
    generate_years_chart(csv_path, viz_dir)
    generate_authors_chart(csv_path, viz_dir)

    logger.info("Dry-run complete. %d mock articles -> %d final", len(mock_articles), len(final))


if __name__ == "__main__":
    main()
