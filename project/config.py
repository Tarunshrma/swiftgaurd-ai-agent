"""
Configuration settings for the SWIFT processing system
"""

import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv

# Udacity workspace: `.env` and `pyproject.toml` live beside `config.py`
_PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(_PROJECT_ROOT / ".env")


class Config:
    """Configuration class for the SWIFT processing system"""

    # OpenAI — read from process environment (e.g. export or `.env` via your shell/IDE).
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

    # System settings
    MESSAGE_COUNT = 10
    BANK_COUNT = 5
    
    # Processing settings
    MAX_WORKERS = 8
    BATCH_SIZE = 50
    
    
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """Get all configuration settings as a dictionary"""
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not attr.startswith('_') and not callable(getattr(cls, attr))
        }
