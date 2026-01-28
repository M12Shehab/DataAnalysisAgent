# app/config.py
"""
Data Analysis Agent - AI-Powered CSV Data Explorer
Copyright (c) 2026 Mohammed Shehab. All rights reserved.

Author: Mohammed Shehab
Email: shihab@live.cn
GitHub: https://github.com/M12Shehab/DataAnalysisAgent
LinkedIn: https://linkedin.com/in/mohammed-shehab

Description:
    Centralized configuration for the Data Analysis Agent application.

License:
    MIT License - see LICENSE file for details

Created: January 2026
Last Modified: January 2026
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    """
    Central application configuration.

    Values are loaded from environment variables with safe defaults.
    """

    # Server / UI
    APP_TITLE: str = os.getenv("APP_TITLE", "Data Analysis Agent")
    APP_DESCRIPTION: str = os.getenv(
        "APP_DESCRIPTION",
        """
Upload a CSV file and interact with an AI-powered agent to explore your data. 
This tool uses LangChain and LLMs to provide safe, sandboxed data analysis without executing arbitrary code.

**Features:**
- 📊 Interactive data exploration and statistics
- 📈 Automated visualization generation
- 🔍 Column search and data profiling
- 🤖 Natural language queries
- 🔒 No arbitrary code execution - tools-only approach

**Supported operations:** Dataset summaries, missing value analysis, descriptive statistics, 
correlation matrices, value counts, and visualizations (histograms, box plots, scatter plots, bar charts).
        """.strip()
    )
    GRADIO_HOST: str = os.getenv("GRADIO_HOST", "0.0.0.0")
    GRADIO_PORT: int = int(os.getenv("GRADIO_PORT", "7860"))
    GRADIO_SHARE: bool = os.getenv("GRADIO_SHARE", "false").lower() == "true"

    # Limits
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

    # Behavior
    RESET_CHAT_ON_UPLOAD: bool = True
    AUTHOR: str = os.getenv("AUTHOR", "Mohammed Shehab")
    COPYRIGHT_YEAR: str = os.getenv("COPYRIGHT_YEAR", "2026")


CONFIG = AppConfig()
