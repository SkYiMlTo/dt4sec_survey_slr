"""
slr/exporters/csv_exporter.py
==============================
Writes the final cleaned article corpus to a CSV file.

Output format
-------------
- UTF-8 with BOM (``utf-8-sig``) so Excel opens it correctly without
  requiring an import wizard
- One row per article; header row included
- Columns: title, authors, publication_year, doi, source, abstract
"""
from __future__ import annotations

import csv
import logging
from pathlib import Path

from slr.models import Article

logger = logging.getLogger(__name__)

_CSV_FIELDNAMES = ["title", "authors", "publication_year", "doi", "source", "abstract"]
_CSV_FILENAME = "articles_final.csv"


def export_csv(articles: list[Article], output_dir: Path) -> Path:
    """Write *articles* to ``<output_dir>/articles_final.csv``.

    Returns the path to the written file.
    """
    output_path = output_dir / _CSV_FILENAME
    with output_path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDNAMES)
        writer.writeheader()
        for article in articles:
            writer.writerow(article.to_dict())

    logger.info("CSV exported: %s (%d articles)", output_path.name, len(articles))
    return output_path
