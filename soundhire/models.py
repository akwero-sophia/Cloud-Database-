"""
Domain models and database operations for SoundHire Cloud.

This module provides functions for CRUD operations on all database tables:
- Packages (sound equipment rental packages)
- Gear (individual equipment items)
- Package-Gear relationships (what's included in each package)
- Bookings (customer reservations)

All functions interact with Supabase PostgreSQL database.
"""

from typing import List, Dict, Optional, Any
# Ensure the supabase package is installed via pip before running the script
# pip install supabase

from supabase import Client
from .db import get_supabase_client

# ============================================================================
# PACKAGE OPERATIONS (CREATE, READ, UPDATE, DELETE)
# ============================================================================

def list_packages(client: Optional[Client] = None) -> List[Dict[str, Any]]:
    """
    Retrieve all rental packages from the database.
    
    Args:
        client: Supabase client (optional, will create if not provided)
        
    Returns:
        List of package dictionaries with id, name, description, daily_rate, stock
    """
    if client is None:
        client = get_supabase_client()
    
    response = client.table("packages").select("*").order("daily_rate").execute()
    return response.data


def get_package_with_contents(package_id: int, client: Optional[Client] = None) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a package including all gear items it contains.
    
    This performs a JOIN query to fetch the package along with all associated
    gear items through the package_gear junction table.
    
    Args:
        package_id: ID of the package to retrieve
        client: Supabase client (optional)
        
    Returns:
        Dictionary with package info and nested 'gear_items' list, or None if not found
    """
    if client is None:
        client = get_supabase_client()
    
    # Get the package basic info
    pkg_response = client.table("packages").select("*").eq("id", package_id).execute()
    
    if not pkg_response.data:
        return None
    
    package = pkg_response.data[0]
    
    # Get associated gear items via junction table
    # This demonstrates working with related tables
    gear_response = (
        client.table("package_gear")
        .select("qty, notes, gear(id, name, category, details)")
        .eq("package_id", package_id)
        .execute()
    )
    
    # Format the gear items for easy display
    package["gear_items"] = gear_response.data
    
    return package


def create_package(
    name: str,
    description: str,
    daily_rate: float,
    stock: int,
    items: List[Dict[str, Any]],
    client: Optional[Client] = None
) -> Dict[str, Any]:
    """
    Create a new rental package with associated gear items.
    
    This function performs multiple INSERT operations:
    1. Insert the package record
    2. Insert package_gear records for each included item
    
    Args:
        name: Package name (e.g., "Deluxe Sound Package")
        description: Detailed package description
        daily_rate: Price per day for this package
        stock: Number of this package available for rent
        items: List of dicts with keys: gear_id, qty, notes (optional)
        client: Supabase client (optional)
        
    Returns:
        The created package dictionary
        
    Example:
        create_package(
            "Custom Package", 
            "For outdoor events",
            200.00,
            2,
            [{"gear_id": 1, "qty": 2, "notes": "Main speakers"}]
        )
    """
    if client is None:
        client = get_supabase_client()
    
    # Insert the package
    pkg_data = {
        "name": name,
        "description": description,
        "daily_rate": daily_rate,
        "stock": stock
    }
    
    pkg_response = client.table("packages").insert(pkg_data).execute()
    package = pkg_response.data[0]
    package_id = package["id"]
    
    # Insert associated gear items
    for item in items:
        gear_data = {
            "package_id": package_id,
            "gear_id": item["gear_id"],
            "qty": item["qty"],
            "notes": item.get("notes", "")
        }
        client.table("package_gear").insert(gear_data).execute()
    
    return package


def update_package(
    package_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    daily_rate: Optional[float] = None,
    stock: Optional[int] = None,
    client: Optional[Client] = None
) -> Dict[str, Any]:
    """
    Update an existing package's information.
    
    Only provided fields will be updated; others remain unchanged.
    
    Args:
        package_id: ID of package to update
        name: New name (optional)
        description: New description (optional)
        daily_rate: New daily rate (optional)
        stock: New stock quantity (optional)
        client: Supabase client (optional)
        
    Returns:
        Updated package dictionary
    """
    if client is None:
        client = get_supabase_client()
    
    # Build update data with only provided fields
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if daily_rate is not None:
        update_data["daily_rate"] = daily_rate
    if stock is not None:
        update_data["stock"] = stock
    
    # Perform the update
    response = (
        client.table("packages")
        .update(update_data)
        .eq("id", package_id)
        .execute()
    )
    
    return response.data[0] if response.data else None


def delete_package(package_id: int, client: Optional[Client] = None) -> bool:
    """
    Delete a package from the database.
    
    Note: This will also delete associated package_gear records due to
    CASCADE constraint, but will fail if there are existing bookings
    due to RESTRICT constraint (which is correct - can't delete packages
    that have been booked).
    
    Args:
        package_id: ID of package to delete
        client: Supabase client (optional)
        
    Returns:
        True if deleted successfully
        
    Raises:
        Exception: If package has existing bookings
    """
    if client is None:
        client = get_supabase_client()
    
    client.table("packages").delete().eq("id", package_id).execute()
    return True


# ============================================================================
# GEAR OPERATIONS
# ============================================================================

def list_gear(client: Optional[Client] = None) -> List[Dict[str, Any]]:
    """
    Get all gear items from the catalog.
    
    Args:
        client: Supabase client (optional)
        
    Returns:
        List of all gear items with their details
    """
    if client is None:
        client = get_supabase_client()
    
    response = client.table("gear").select("*").order("category, name").execute()
    return response.data


# ============================================================================
# BOOKING OPERATIONS
# ============================================================================

def create_booking(
    package_id: int,
    customer_name: str,
    phone: str,
    email: str,
    start_date: str,
    end_date: str,
    qty: int,
    include_dj: bool,
    total_price: float,
    client: Optional[Client] = None
) -> Dict[str, Any]:
    """
    Create a new booking reservation.
    
    Note: This function does NOT check availability - use the availability
    module's functions before calling this to ensure the booking is valid.
    
    Args:
        package_id: ID of package being rented
        customer_name: Customer's full name
        phone: Contact phone number
        email: Contact email address
        start_date: Rental start date (YYYY-MM-DD format)
        end_date: Rental end date (YYYY-MM-DD format)
        qty: Number of packages being rented
        include_dj: Whether DJ service is included
        total_price: Calculated total price for the booking
        client: Supabase client (optional)
        
    Returns:
        Created booking dictionary
    """
    if client is None:
        client = get_supabase_client()
    
    booking_data = {
        "package_id": package_id,
        "customer_name": customer_name,
        "phone": phone,
        "email": email,
        "start_date": start_date,
        "end_date": end_date,
        "qty": qty,
        "include_dj": include_dj,
        "total_price": total_price,
        "status": "pending"
    }
    
    response = client.table("bookings").insert(booking_data).execute()
    return response.data[0]


def list_bookings(client: Optional[Client] = None) -> List[Dict[str, Any]]:
    """
    Retrieve all bookings with package information.
    
    This performs a JOIN to include package details with each booking.
    
    Args:
        client: Supabase client (optional)
        
    Returns:
        List of bookings with nested package information
    """
    if client is None:
        client = get_supabase_client()
    
    response = (
        client.table("bookings")
        .select("*, packages(name)")
        .order("created_at", desc=True)
        .execute()
    )
    
    return response.data


def get_bookings_for_package(
    package_id: int,
    start_date: str,
    end_date: str,
    client: Optional[Client] = None
) -> List[Dict[str, Any]]:
    """
    Get all bookings that overlap with a given date range for a package.
    
    This is used for availability checking. Two bookings overlap if:
    requested_start <= existing_end AND requested_end >= existing_start
    
    Args:
        package_id: Package to check
        start_date: Start of date range to check (YYYY-MM-DD)
        end_date: End of date range to check (YYYY-MM-DD)
        client: Supabase client (optional)
        
    Returns:
        List of overlapping bookings (excluding cancelled ones)
    """
    if client is None:
        client = get_supabase_client()
    
    # Query for overlapping bookings
    # A booking overlaps if: start_date <= their_end AND end_date >= their_start
    response = (
        client.table("bookings")
        .select("*")
        .eq("package_id", package_id)
        .neq("status", "cancelled")  # Don't count cancelled bookings
        .lte("start_date", end_date)  # Their start is before or on our end
        .gte("end_date", start_date)  # Their end is after or on our start
        .execute()
    )
    
    return response.data


# ============================================================================
# SETTINGS OPERATIONS
# ============================================================================

def get_dj_rate(client: Optional[Client] = None) -> float:
    """
    Get the current DJ daily rate from settings.
    
    Args:
        client: Supabase client (optional)
        
    Returns:
        DJ daily rate as a float
    """
    if client is None:
        client = get_supabase_client()
    
    response = client.table("settings").select("dj_daily_rate").eq("id", 1).execute()
    
    if response.data:
        return float(response.data[0]["dj_daily_rate"])
    
    # Default if not set (shouldn't happen with proper seed data)
    return 150.00