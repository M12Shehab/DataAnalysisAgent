# app/tools/stats.py
from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd
from app.state import STATE


def _require_df() -> pd.DataFrame:
    """
    Internal helper: return the active DataFrame or raise a clear error.

    Raises:
        ValueError: If no dataset is loaded in STATE.df.
    """
    if STATE.df is None:
        raise ValueError("No dataset loaded. Upload a CSV first.")
    return STATE.df


def describe_columns(columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Compute descriptive statistics for the dataset (or selected columns).

    For numeric columns, returns count/mean/std/min/quartiles/max.
    For non-numeric columns, returns count/unique/top/freq when applicable.

    Args:
        columns (list[str] | None, optional):
            - If provided: compute stats only for these columns.
            - If None: compute stats for all columns.
            Default: None.

    Returns:
        dict: JSON-serializable nested dict produced from pandas `describe(include="all")`.
        Structure roughly:
            {
              "colA": {"count": ..., "mean": ..., ...},
              "colB": {"count": ..., "unique": ..., ...},
              ...
            }
        (Exact keys depend on data types.)

    Raises:
        ValueError:
            - If no dataset is loaded.
            - If any requested column is not in the dataset.

    Notes:
        - Missing values may be represented as empty strings in the output for JSON safety.
        - For very wide datasets, consider specifying a subset of columns.

    Example:
        >>> describe_columns(["age", "fare"])
        {
          "age": {"count": 714.0, "mean": 29.7, ...},
          "fare": {"count": 891.0, "mean": 32.2, ...}
        }
    """
    df = _require_df()

    if columns is not None:
        missing = [c for c in columns if c not in df.columns]
        if missing:
            raise ValueError(f"Invalid columns: {missing}")
        df = df[columns]

    desc = df.describe(include="all")
    # Make JSON-safe: NaN -> "" (or you could choose None)
    desc = desc.fillna("")
    return desc.to_dict()


def missing_values() -> Dict[str, int]:
    """
    Return missing (NA/NaN) value counts per column.

    Args:
        None.

    Returns:
        dict[str, int]: Column -> number of missing values.

    Raises:
        ValueError: If no dataset is loaded.

    Example:
        >>> missing_values()
        {"age": 177, "cabin": 687, "fare": 0}
    """
    df = _require_df()
    return {col: int(df[col].isna().sum()) for col in df.columns}


def value_counts(column: str, limit: int = 10) -> Dict[str, int]:
    """
    Compute value counts for a single column (top-N).

    Best for categorical/text columns. For numeric columns, it can still work
    but may have too many unique values.

    Args:
        column (str): Column name to count values for.
        limit (int, optional): Maximum number of most frequent values to return.
            - Minimum: 1
            - Maximum: 20
            - Default: 10

    Returns:
        dict[str, int]: Value -> count, limited to top-N. Values are converted to strings
        to keep JSON output stable (e.g., timestamps, mixed types).

    Raises:
        ValueError:
            - If no dataset is loaded.
            - If column does not exist.

    Example:
        >>> value_counts("sex", limit=2)
        {"male": 577, "female": 314}
    """
    df = _require_df()
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist")

    limit = int(limit)
    limit = max(1, min(limit, 20))

    vc = df[column].value_counts(dropna=False).head(limit)
    return {str(k): int(v) for k, v in vc.items()}


def correlation_matrix(method: str = "pearson") -> Dict[str, Dict[str, float]]:
    """
    Compute correlation matrix for numeric columns only.

    Args:
        method (str, optional): Correlation method.
            Supported: "pearson", "spearman", "kendall".
            Default: "pearson".

    Returns:
        dict[str, dict[str, float]]: Nested dict representing the correlation matrix,
        rounded to 4 decimals:
            {
              "col1": {"col1": 1.0, "col2": 0.12, ...},
              "col2": {"col1": 0.12, "col2": 1.0, ...}
            }

    Raises:
        ValueError:
            - If no dataset is loaded.
            - If method is not supported.
            - If fewer than 2 numeric columns exist.

    Notes:
        - Correlation uses pairwise complete observations (pandas default).
        - For very large datasets, this may be slower.

    Example:
        >>> correlation_matrix()
        {"age": {"age": 1.0, "fare": 0.09}, "fare": {"age": 0.09, "fare": 1.0}}
    """
    df = _require_df()

    method = (method or "pearson").strip().lower()
    if method not in {"pearson", "spearman", "kendall"}:
        raise ValueError("method must be one of: pearson, spearman, kendall")

    num_df = df.select_dtypes(include="number")
    if num_df.shape[1] < 2:
        raise ValueError("Not enough numeric columns for correlation (need at least 2).")

    corr = num_df.corr(method=method).round(4)
    return corr.to_dict()
