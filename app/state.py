# app/state.py
import pandas as pd
from typing import Optional

class AppState:
    df: Optional[pd.DataFrame] = None
    dataset_name: Optional[str] = None

STATE = AppState()
