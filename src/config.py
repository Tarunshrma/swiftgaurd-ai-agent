"""
Configuration settings for the SWIFT processing system
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for the SWIFT processing system"""
    
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
