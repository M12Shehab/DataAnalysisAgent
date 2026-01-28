# app/tools/visualization.py
"""
Data Analysis Agent - AI-Powered CSV Data Explorer
Copyright (c) 2026 Mohammed Shehab. All rights reserved.

Author: Mohammed Shehab
Email: shihab@live.cn
GitHub: https://github.com/M12Shehab/DataAnalysisAgent
LinkedIn: https://linkedin.com/in/mohammed-shehab

Description:
    Visualization tool functions for the Data Analysis Agent.
    It provides safe, predefined plotting capabilities to avoid arbitrary code execution.
    It supports histograms, box plots, scatter plots, and bar charts. You can add more plot types as needed.

License:
    MIT License - see LICENSE file for details

Created: January 2026
Last Modified: January 2026
"""
from __future__ import annotations

from typing import Optional
import uuid
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from app.state import STATE

ALLOWED_PLOTS = {"hist", "box", "scatter", "bar"}
MAX_CATEGORIES_BAR = 10


def _require_df() -> pd.DataFrame:
    """
    Internal helper: return the active DataFrame or raise a clear error.

    Raises:
        ValueError: If no dataset is loaded in STATE.df.
    """
    if STATE.df is None:
        raise ValueError("No dataset loaded. Upload a CSV first.")
    return STATE.df


def plot(kind: str, column_x: str, column_y: Optional[str] = None) -> str:
    """
    Create a SAFE, predefined plot from the dataset and return the image file path.

    This tool intentionally restricts plot types to avoid arbitrary code execution.
    Use it to generate quick EDA visualizations.

    Args:
        kind (str): Plot type (restricted). Must be one of:
            - "hist": Histogram of a single column
            - "box": Box plot of a single column
            - "scatter": Scatter plot between column_x and column_y
            - "bar": Bar plot of top categories for column_x
        column_x (str): Primary column name for the plot.
        column_y (str | None, optional): Second column name (required for "scatter").
            Default: None.

    Returns:
        str: Absolute path to a saved PNG image in /tmp (inside the container),
        for example: "/tmp/plot_abc123.png".

    Raises:
        ValueError:
            - If no dataset is loaded.
            - If kind is not allowed.
            - If specified columns do not exist.
            - If kind == "scatter" and column_y is missing.

    Behavior / Constraints:
        - Output is always a PNG.
        - For "bar", only the top 10 categories are plotted.
        - The function does NOT return raw image bytes, only the file path.
        - Caller (Gradio) should load/display the returned file.

    Examples:
        >>> plot("hist", "age")
        "/tmp/plot_9f2c...png"

        >>> plot("scatter", "height", "weight")
        "/tmp/plot_1a7b...png"
    """
    df = _require_df()

    kind = (kind or "").strip().lower()
    if kind not in ALLOWED_PLOTS:
        raise ValueError(f"Plot type must be one of: {sorted(ALLOWED_PLOTS)}")

    if column_x not in df.columns:
        raise ValueError(f"Column '{column_x}' does not exist")

    if kind == "scatter":
        if not column_y:
            raise ValueError("column_y is required for scatter plots")
        if column_y not in df.columns:
            raise ValueError(f"Column '{column_y}' does not exist")

    plt.figure(figsize=(6, 4))

    if kind == "hist":
        series = df[column_x].dropna()
        series.hist(bins=30)

    elif kind == "box":
        sns.boxplot(x=df[column_x])

    elif kind == "scatter":
        sns.scatterplot(x=df[column_x], y=df[column_y])

    elif kind == "bar":
        vc = df[column_x].value_counts(dropna=False).head(MAX_CATEGORIES_BAR)
        sns.barplot(x=vc.index.astype(str), y=vc.values)
        plt.xticks(rotation=45, ha="right")

    plt.tight_layout()

    filename = f"/tmp/plot_{uuid.uuid4().hex}.png"
    plt.savefig(filename)
    plt.close()
    return filename
