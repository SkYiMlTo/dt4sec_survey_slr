"""
utils/logging_config.py
=======================
Centralised logging setup for the SLR pipeline.

Call ``setup_logging()`` once at application startup.  All modules should
then obtain a logger via ``logging.getLogger(__name__)``.

Features
--------
- Coloured console output (via ``rich``) in development
- Plain-text file log written to ``<run_dir>/slr_pipeline.log``
- Structured JSON log written to ``<run_dir>/slr_pipeline.jsonl``
  (machine-readable; useful for CI artifact parsing)
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# JSON log handler
# ---------------------------------------------------------------------------


class _JsonFileHandler(logging.FileHandler):
    """Appends structured JSON lines to a log file."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry: dict[str, Any] = {
                "ts": datetime.now(tz=timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "msg": record.getMessage(),
            }
            if record.exc_info:
                entry["exc"] = self.formatException(record.exc_info)
            self.stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self.flush()
        except Exception:  # pragma: no cover  # noqa: BLE001
            self.handleError(record)


# ---------------------------------------------------------------------------
# Console handler — use ``rich`` if available, else plain stderr
# ---------------------------------------------------------------------------


def _make_console_handler() -> logging.Handler:
    try:
        from rich.logging import RichHandler  # type: ignore[import-untyped]

        return RichHandler(
            rich_tracebacks=True,
            show_time=True,
            show_path=False,
            markup=True,
        )
    except ModuleNotFoundError:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        return handler


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def setup_logging(
    run_dir: Path | None = None,
    level: int = logging.INFO,
) -> None:
    """Configure the root logger.

    Parameters
    ----------
    run_dir:
        If provided, a plain-text ``.log`` file and a JSON ``.jsonl`` file
        will be written inside this directory.
    level:
        Root log level (default: ``INFO``).
    """
    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers on repeated calls (e.g., in tests)
    if root.handlers:
        root.handlers.clear()

    # Console
    console = _make_console_handler()
    console.setLevel(level)
    root.addHandler(console)

    if run_dir is not None:
        run_dir.mkdir(parents=True, exist_ok=True)

        # Plain-text file
        txt_handler = logging.FileHandler(
            run_dir / "slr_pipeline.log", encoding="utf-8"
        )
        txt_handler.setLevel(level)
        txt_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        root.addHandler(txt_handler)

        # JSON lines file
        json_handler = _JsonFileHandler(
            run_dir / "slr_pipeline.jsonl", encoding="utf-8"
        )
        json_handler.setLevel(level)
        root.addHandler(json_handler)

    # Silence noisy third-party loggers
    for noisy in ("urllib3", "selenium", "httpx", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
