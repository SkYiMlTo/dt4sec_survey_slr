"""
slr/visualization/authors_chart.py
=====================================
Generates a horizontal bar chart of the top-N authors by publication count.

Improvements over the legacy version
--------------------------------------
- Reads from ``articles_final.csv`` (not Excel)
- Handles ``"No authors"`` sentinel rows gracefully
- Uses ``matplotlib`` ``Agg`` backend for headless CI
- Horizontal bar chart for better readability of long author names
- Configurable top-N parameter (default 10)
"""
from __future__ import annotations

import csv
import logging
from collections import Counter
from pathlib import Path

logger = logging.getLogger(__name__)

_OUTPUT_FILENAME = "plt_top_authors.png"
_DEFAULT_TOP_N = 10


def generate_authors_chart(
    csv_path: Path,
    output_dir: Path,
    top_n: int = _DEFAULT_TOP_N,
) -> Path | None:
    """Read *csv_path* and save a top-N authors horizontal bar chart.

    Returns the path to the saved PNG, or ``None`` on failure.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    author_counter: Counter[str] = Counter()

    try:
        with csv_path.open(encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                raw_authors = (row.get("authors") or "").strip()
                if not raw_authors or raw_authors.lower() == "no authors":
                    continue
                for name in raw_authors.split(","):
                    name = name.strip()
                    if name:
                        author_counter[name] += 1
    except Exception as exc:  # noqa: BLE001
        logger.error("Authors chart — failed to read CSV: %s", exc)
        return None

    if not author_counter:
        logger.warning("Authors chart — no authors found; skipping chart")
        return None

    top_authors = author_counter.most_common(top_n)
    names, counts = zip(*reversed(top_authors))  # reversed for bottom-to-top bars

    fig, ax = plt.subplots(figsize=(10, max(4, top_n * 0.5)))

    bars = ax.barh(
        list(names),
        list(counts),
        color="#2CA02C",
        edgecolor="white",
        linewidth=0.8,
    )

    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_width() + 0.05,
            bar.get_y() + bar.get_height() / 2,
            str(count),
            va="center",
            fontsize=9,
            color="#333333",
        )

    ax.set_xlabel("Number of Publications", fontsize=12)
    ax.set_ylabel("Author", fontsize=12)
    ax.set_title(f"Top {top_n} Authors by Publication Count", fontsize=14, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.grid(True, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()

    output_path = output_dir / _OUTPUT_FILENAME
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    logger.info("Authors chart saved: %s", output_path.name)
    return output_path
