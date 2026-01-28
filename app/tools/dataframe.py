# app/tools/dataframe.py
from __future__ import annotations

from typing import Any, Dict, List
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


def dataset_summary() -> Dict[str, Any]:
    """
    Return a high-level overview of the currently loaded dataset.

    Use this tool first when you need quick context about the dataset shape,
    column names, and data types.

    Args:
        None.

    Returns:
        dict: A JSON-serializable dictionary with:
            - rows (int): Number of rows.
            - columns (int): Number of columns.
            - column_names (list[str]): Column names in order.
            - dtypes (dict[str, str]): Column -> pandas dtype as a string.
            - dataset_name (str|None): Optional name if provided at load time.

    Raises:
        ValueError: If no dataset is loaded.

    Notes:
        - This tool does NOT return any row-level data (only metadata).
        - Safe to call frequently.

    Example:
        >>> dataset_summary()
        {
          "rows": 891,
          "columns": 12,
          "column_names": ["age", "fare", ...],
          "dtypes": {"age": "float64", "fare": "float64", ...},
          "dataset_name": "titanic.csv"
        }
    """
    df = _require_df()
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "dataset_name": STATE.dataset_name,
    }


def sample_rows(n: int = 5) -> List[Dict[str, Any]]:
    """
    Return a small sample of the first N rows of the dataset.

    Use this tool when you need to inspect actual values, spot obvious issues,
    or infer semantics from the data. This tool is bounded for safety.

    Args:
        n (int, optional): Number of rows to return from the top of the dataset.
            - Minimum: 1
            - Maximum: 20
            - Default: 5

    Returns:
        list[dict]: A list of row objects (records). Each dict maps column name -> value.
        The output is JSON-serializable.

    Raises:
        ValueError: If no dataset is loaded.

    Constraints:
        - Returns at most 20 rows to prevent large outputs.
        - Always returns from the start of the dataset (head).

    Example:
        >>> sample_rows(2)
        [
          {"age": 22, "fare": 7.25, "sex": "male"},
          {"age": 38, "fare": 71.28, "sex": "female"}
        ]
    """
    df = _require_df()
    n = int(n)
    n = max(1, min(n, 20))
    return df.head(n).to_dict(orient="records")


def find_columns(keyword: str) -> List[str]:
    """
    Find column names containing a keyword (case-insensitive).

    Use this tool when the user references a concept (e.g., "price", "salary")
    and you need to locate matching columns.

    Args:
        keyword (str): Text to search for in column names. Case-insensitive.
            Leading/trailing spaces are ignored.

    Returns:
        list[str]: Matching column names in their original order. Empty list if none.

    Raises:
        ValueError: If no dataset is loaded.

    Example:
        >>> find_columns("date")
        ["created_date", "signup_date"]
    """
    df = _require_df()
    kw = (keyword or "").strip().lower()
    if not kw:
        return []
    return [c for c in df.columns if kw in c.lower()]
