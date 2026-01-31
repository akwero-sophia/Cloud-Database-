"""
Database connection handling for SoundHire Cloud.

Manages the Supabase client connection used across the entire application.
Keeps things simple with a singleton pattern so we're not creating
multiple connections unnecessarily.
"""

from typing import Optional
from supabase import create_client, Client
from .config import get_supabase_url, get_supabase_key


# Single client instance shared across the app
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Gets or creates the Supabase client.
    
    Uses singleton pattern - creates once on first call, then reuses it.
    This keeps things efficient and maintains proper connection pooling.
    
    Returns:
        Ready-to-use Supabase client
        
    Raises:
        ValueError: When config is messed up
        Exception: When we can't connect to Supabase
    """
    global _supabase_client
    
    # If we already have a client, just return it
    if _supabase_client is not None:
        return _supabase_client
    
    try:
        # Pull credentials from environment
        url = get_supabase_url()
        key = get_supabase_key()
        
        # Set up the Supabase client
        _supabase_client = create_client(url, key)
        
        return _supabase_client
        
    except ValueError as e:
        # Something's wrong with the config
        raise ValueError(
            f"Couldn't configure Supabase client: {str(e)}\n"
            "Check your .env file."
        ) from e
    except Exception as e:
        # Can't connect for some reason
        raise Exception(
            f"Failed to connect to Supabase: {str(e)}\n"
            "Verify your Supabase URL and API key."
        ) from e


def reset_client() -> None:
    """
    Resets the global client - mainly useful for testing.
    """
    global _supabase_client
    _supabase_client = None