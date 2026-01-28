# app/state.py
"""
Data Analysis Agent - AI-Powered CSV Data Explorer
Copyright (c) 2026 Mohammed Shehab. All rights reserved.

Author: Mohammed Shehab
Email: shihab@live.cn
GitHub: https://github.com/M12Shehab/DataAnalysisAgent
LinkedIn: https://linkedin.com/in/mohammed-shehab

Description:
    Application state management for the Data Analysis Agent.
License:
    MIT License - see LICENSE file for details

Created: January 2026
Last Modified: January 2026
"""
import pandas as pd
from typing import Optional

class AppState:
    df: Optional[pd.DataFrame] = None
    dataset_name: Optional[str] = None

STATE = AppState()
