"""
Utility functions for the AI Travel Agent application
"""
import os
import streamlit as st


def get_env_var(key, default=None):
    """
    Get environment variable from either Streamlit secrets (deployment) or os.environ (local)
    
    Args:
        key (str): Environment variable key
        default: Default value if key is not found
        
    Returns:
        str: Environment variable value or default
    """
    try:
        # Try Streamlit secrets first (for deployment)
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    # Fallback to os.environ (for local development)
    return os.environ.get(key, default)