"""Environment utilities for the AI Travel Agent application"""
import os
from typing import Optional


def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable from os.environ
    
    Args:
        key: Environment variable key
        default: Default value if not found
        
    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default)