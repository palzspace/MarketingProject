"""Chart generation from query results.

Uses the non-interactive Agg backend so Streamlit can safely render
figures as in-memory PNG images.
"""

import io
import logging

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

logger = logging.getLogger(__name__)

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "#f9f9f9",
        "axes.grid": True,
        "grid.alpha": 0.3,
    }
)

_VALID_CHART_TYPES = {"bar", "line", "histogram", "pie"}


def create_chart(
    df: pd.DataFrame,
    chart_type: str,
    title: str = "",
    x_col: str | None = None,
    y_col: str | None = None,
) -> io.BytesIO:
    """Create a chart and return it as a PNG bytes buffer."""
    chart_type = chart_type.lower().strip()
    if chart_type not in _VALID_CHART_TYPES:
        logger.warning("Unknown chart type '%s' — falling back to bar.", chart_type)
        chart_type = "bar"

    x_col, y_col = _resolve_columns(df, x_col, y_col)

    fig, ax = plt.subplots(figsize=(10, 6))

    draw = {
        "bar": _draw_bar,
        "line": _draw_line,
        "histogram": _draw_histogram,
        "pie": _draw_pie,
    }
    draw[chart_type](ax, df, x_col, y_col)

    ax.set_title(title or f"{y_col} by {x_col}", fontsize=14, fontweight="bold")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    buf.seek(0)
    plt.close(fig)

    logger.info("Created %s chart: %s", chart_type, title)
    return buf


# ── Private helpers (one per chart type) ─────────────────────────────────


def _resolve_columns(
    df: pd.DataFrame,
    x_col: str | None,
    y_col: str | None,
) -> tuple[str, str | None]:
    """Pick sensible default columns when the caller didn't specify."""
    if x_col is None:
        x_col = df.columns[0]
    if y_col is None and len(df.columns) > 1:
        numeric = df.select_dtypes(include="number").columns
        y_col = numeric[0] if len(numeric) > 0 else df.columns[1]
    return x_col, y_col


def _draw_bar(ax, df: pd.DataFrame, x: str, y: str) -> None:
    ax.bar(df[x].astype(str), df[y], color="#4C9AFF", edgecolor="white")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")


def _draw_line(ax, df: pd.DataFrame, x: str, y: str) -> None:
    ax.plot(df[x], df[y], marker="o", linewidth=2, color="#36B37E")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")


def _draw_histogram(ax, df: pd.DataFrame, _x: str, y: str) -> None:
    col = y or _x
    ax.hist(df[col], bins=15, color="#6554C0", edgecolor="white")
    ax.set_xlabel(col)
    ax.set_ylabel("Frequency")


def _draw_pie(ax, df: pd.DataFrame, x: str, y: str) -> None:
    ax.pie(df[y], labels=df[x].astype(str), autopct="%1.1f%%", startangle=140)
    ax.set_ylabel("")
