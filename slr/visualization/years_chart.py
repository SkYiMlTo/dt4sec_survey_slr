"""
slr/visualization/years_chart.py
==================================
Generates a bar chart of article publications per year.

Improvements over the legacy version
--------------------------------------
- Reads from the unified ``articles_final.csv`` (not the Excel workbook)
- Filters out non-numeric / out-of-range year values gracefully
- Uses ``matplotlib`` non-interactive backend (``Agg``) so it runs safely
  in headless CI environments without a display
- Applies a modern style with a custom colour palette
"""
from __future__ import annotations

import csv
import logging
from collections import Counter
from pathlib import Path

logger = logging.getLogger(__name__)

_MIN_YEAR = 1990
_MAX_YEAR = 2100
_OUTPUT_FILENAME = "plt_publications_per_year.png"


def generate_years_chart(csv_path: Path, output_dir: Path) -> Path | None:
    """Read *csv_path* and save a publications-per-year bar chart.

    Returns the path to the saved PNG, or ``None`` on failure.
    """
    import matplotlib
    matplotlib.use("Agg")  # headless — must be set before importing pyplot
    import matplotlib.pyplot as plt

    years: list[int] = []

    try:
        with csv_path.open(encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                raw_year = (row.get("publication_year") or "").strip()
                if not raw_year:
                    continue
                try:
                    year = int(raw_year)
                except ValueError:
                    logger.debug("Skipping non-numeric year: %r", raw_year)
                    continue
                if _MIN_YEAR <= year <= _MAX_YEAR:
                    years.append(year)
                else:
                    logger.debug("Skipping out-of-range year: %d", year)
    except Exception as exc:  # noqa: BLE001
        logger.error("Years chart — failed to read CSV: %s", exc)
        return None

    if not years:
        logger.warning("Years chart — no valid years found; skipping chart")
        return None

    counts = Counter(years)
    sorted_years = sorted(counts.keys())
    sorted_counts = [counts[y] for y in sorted_years]

    fig, ax = plt.subplots(figsize=(12, 6))

    bars = ax.bar(
        [str(y) for y in sorted_years],
        sorted_counts,
        color="#1F77B4",
        edgecolor="white",
        linewidth=0.8,
    )

    # Value labels on top of each bar
    for bar, count in zip(bars, sorted_counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.1,
            str(count),
            ha="center",
            va="bottom",
            fontsize=9,
            color="#333333",
        )

    ax.set_xlabel("Publication Year", fontsize=12)
    ax.set_ylabel("Number of Publications", fontsize=12)
    ax.set_title("Distribution of Publications by Year", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=45)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()

    output_path = output_dir / _OUTPUT_FILENAME
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    logger.info("Years chart saved: %s", output_path.name)
    return output_path
