"""
slr/extractors/base.py
======================
Abstract base class that every database extractor must implement.

Contract
--------
- ``extract(query)`` must return a ``list[Article]`` (may be empty).
- It must NEVER raise an unhandled exception; catch everything and log.
- The ``name`` class attribute is used for logging and output file naming.
"""
from __future__ import annotations

import abc
import logging
from pathlib import Path
from typing import Final

from slr.models import Article

logger = logging.getLogger(__name__)


class BaseExtractor(abc.ABC):
    """Abstract database extractor.

    Subclasses must override :meth:`extract`.

    Parameters
    ----------
    output_dir:
        Directory where the raw JSON result file will be saved.
        Passed in by the pipeline so every extractor writes its own file.
    """

    #: Short, filesystem-safe name used for log messages and output files.
    name: str = "base"

    #: Human-readable URL of the database being scraped.
    source_url: str = ""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self._log = logging.getLogger(f"slr.extractors.{self.name}")

    @abc.abstractmethod
    def extract(self, query: str) -> list[Article]:
        """Run the extraction for *query* and return a list of articles.

        Implementations must:
        - Handle all HTTP / Selenium / parsing errors internally.
        - Return an empty list (not raise) on total failure.
        - Persist a raw JSON snapshot to ``self.output_dir / <name>.json``.
        """

    def _save_raw(self, articles: list[Article]) -> None:
        """Write raw extraction results to ``<output_dir>/<name>.json``."""
        import json

        path = self.output_dir / f"{self.name}.json"
        data = [
            {
                "title": a.title,
                "authors": a.authors,
                "publicationYear": a.publication_year,
                "doi": a.doi,
                "source": a.source,
                "abstract": a.abstract,
            }
            for a in articles
        ]
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self._log.info(
            "Saved %d raw articles -> %s", len(articles), path.name
        )
