"""Chart generation from query results.

Keeps Matplotlib in the non-interactive Agg backend so Streamlit
can safely render the figures as images.
"""

import io
import logging

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

logger = logging.getLogger(__name__)

# A little visual polish never hurt anyone
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
    """Create a chart and return it as a PNG bytes buffer.

    Parameters
    ----------
    df : DataFrame with query results.
    chart_type : One of bar, line, histogram, pie.
    title : Chart title.
    x_col / y_col : Column names for the axes. Auto-detected when *None*.
    """
    chart_type = chart_type.lower().strip()
    if chart_type not in _VALID_CHART_TYPES:
        logger.warning("Unknown chart type '%s' — falling back to bar.", chart_type)
        chart_type = "bar"

    x_col, y_col = _resolve_columns(df, x_col, y_col)

    fig, ax = plt.subplots(figsize=(10, 6))

    if chart_type == "bar":
        _draw_bar(ax, df, x_col, y_col)
    elif chart_type == "line":
        _draw_line(ax, df, x_col, y_col)
    elif chart_type == "histogram":
        _draw_histogram(ax, df, y_col or x_col)
    elif chart_type == "pie":
        _draw_pie(ax, df, x_col, y_col)

    ax.set_title(title or f"{y_col} by {x_col}", fontsize=14, fontweight="bold")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    buf.seek(0)
    plt.close(fig)

    logger.info("Created %s chart: %s", chart_type, title)
    return buf


# ---------------------------------------------------------------------------
# Private helpers — one per chart type keeps things readable
# ---------------------------------------------------------------------------

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


def _draw_histogram(ax, df: pd.DataFrame, col: str) -> None:
    ax.hist(df[col], bins=15, color="#6554C0", edgecolor="white")
    ax.set_xlabel(col)
    ax.set_ylabel("Frequency")


def _draw_pie(ax, df: pd.DataFrame, x: str, y: str) -> None:
    ax.pie(df[y], labels=df[x].astype(str), autopct="%1.1f%%", startangle=140)
    ax.set_ylabel("")  # pie charts don't need a y-label
