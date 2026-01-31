"""
Configuration management for SoundHire Cloud.

Handles environment variables and Supabase credentials. The .env file
contains sensitive data like API keys, so it's excluded from git.
Make sure you've created your .env file with valid Supabase credentials
before running the app.
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv


def load_environment() -> None:
    """
    Loads environment variables from .env file.
    Called at startup to make configuration available throughout the app.
    """
    load_dotenv()


def get_settings() -> Dict[str, Optional[str]]:
    """
    Grabs application settings from environment variables.
    
    Returns:
        Dictionary with SUPABASE_URL and SUPABASE_KEY
        
    Raises:
        ValueError: When required variables aren't set
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    # Make sure we have the credentials we need
    if not supabase_url or not supabase_key:
        raise ValueError(
            "Missing required environment variables. "
            "Make sure SUPABASE_URL and SUPABASE_ANON_KEY are in your .env file. "
            "Check .env.example if you need a template."
        )
    
    # Quick sanity check on the URL format
    if not supabase_url.startswith("https://"):
        raise ValueError(
            "SUPABASE_URL needs to be a valid HTTPS URL. "
            "Double-check your Supabase project settings."
        )
    
    return {
        "SUPABASE_URL": supabase_url,
        "SUPABASE_KEY": supabase_key
    }


def get_supabase_url() -> str:
    """Gets the Supabase project URL from environment."""
    return get_settings()["SUPABASE_URL"]


def get_supabase_key() -> str:
    """Gets the Supabase API key (anon or service role)."""
    return get_settings()["SUPABASE_KEY"]