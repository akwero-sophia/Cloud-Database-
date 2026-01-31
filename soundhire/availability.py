"""
Availability and pricing logic for SoundHire rentals.

Handles the important stuff:
- Figuring out if a package is available for certain dates
- Calculating total prices (equipment + optional DJ service)
- Working out how many rental days we're dealing with
"""

from datetime import datetime, date
from typing import Optional
from supabase import Client
from .models import get_bookings_for_package, get_dj_rate
from .db import get_supabase_client


def calculate_rental_days(start_date: str, end_date: str) -> int:
    """
    Counts rental days - includes both start and end dates.
    
    So Nov 10 to Nov 12 = 3 days (the 10th, 11th, and 12th)
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        Number of days (at least 1)
        
    Example:
        calculate_rental_days("2025-11-10", "2025-11-12") → 3 days
        calculate_rental_days("2025-11-10", "2025-11-10") → 1 day
    """
    # Convert strings to actual dates
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # Add 1 because we include both endpoints
    days = (end - start).days + 1
    
    # Always at least 1 day
    return max(1, days)


def is_package_available(
    package_id: int,
    start_date: str,
    end_date: str,
    qty: int,
    client: Optional[Client] = None
) -> tuple[bool, str]:
    """
    Checks if we have enough packages available for the requested dates.
    
    Here's what we do:
    1. Look up how many of this package we have in stock
    2. Find all bookings that overlap with the requested dates
    3. Add up how many are already booked during that time
    4. See if we have enough left over
    
    Bookings overlap when:
        requested_start <= their_end AND requested_end >= their_start
    
    Args:
        package_id: Which package to check
        start_date: When they want to start (YYYY-MM-DD)
        end_date: When they're done (YYYY-MM-DD)
        qty: How many they need
        client: Supabase client (optional)
        
    Returns:
        (available?, message explaining why or why not)
        
    Example:
        available, msg = is_package_available(1, "2025-11-10", "2025-11-12", 1)
        if available:
            # Good to go - make the booking
        else:
            print(f"Sorry: {msg}")
    """
    if client is None:
        client = get_supabase_client()
    
    # Look up the package
    pkg_response = client.table("packages").select("name, stock").eq("id", package_id).execute()
    
    if not pkg_response.data:
        return False, f"Package {package_id} not found"
    
    package = pkg_response.data[0]
    stock = package["stock"]
    package_name = package["name"]
    
    # Quick check - do we even have that many total?
    if qty > stock:
        return False, f"Requested quantity ({qty}) exceeds total stock ({stock}) for {package_name}"
    
    # Find bookings that clash with these dates
    overlapping_bookings = get_bookings_for_package(package_id, start_date, end_date, client)
    
    # See how many are already spoken for
    booked_qty = sum(booking["qty"] for booking in overlapping_bookings)
    
    # What's left?
    remaining = stock - booked_qty
    
    if qty > remaining:
        return False, (
            f"Not enough {package_name} available. "
            f"You need: {qty}, We have: {remaining} "
            f"(already booked: {booked_qty}/{stock})"
        )
    
    # We're good!
    return True, f"{package_name} is available ({remaining} of {stock} free for these dates)"


def calculate_total_price(
    package_id: int,
    start_date: str,
    end_date: str,
    qty: int,
    include_dj: bool,
    client: Optional[Client] = None
) -> tuple[float, dict]:
    """
    Figures out how much a rental will cost.
    
    Price breakdown:
    - Equipment: daily_rate × days × quantity
    - DJ service (optional): dj_rate × days × quantity
    - Total: equipment + DJ (if added)
    
    Args:
        package_id: Which package they're renting
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        qty: How many packages
        include_dj: Add DJ service?
        client: Supabase client (optional)
        
    Returns:
        (total_price, detailed_breakdown_dict)
        
        Breakdown includes:
            days, daily_rate, qty, base_price,
            dj_rate, dj_price, total
            
    Example:
        total, breakdown = calculate_total_price(1, "2025-11-10", "2025-11-12", 1, True)
        print(f"Total: ${total:.2f}")
    """
    if client is None:
        client = get_supabase_client()
    
    # Get the package rate
    pkg_response = client.table("packages").select("daily_rate").eq("id", package_id).execute()
    
    if not pkg_response.data:
        raise ValueError(f"Package {package_id} not found")
    
    daily_rate = float(pkg_response.data[0]["daily_rate"])
    
    # How many days?
    days = calculate_rental_days(start_date, end_date)
    
    # Base equipment cost
    base_price = daily_rate * days * qty
    
    # Start building the breakdown
    breakdown = {
        "days": days,
        "daily_rate": daily_rate,
        "qty": qty,
        "base_price": base_price,
        "dj_rate": 0.0,
        "dj_price": 0.0,
        "total": base_price
    }
    
    # Tack on DJ cost if they want it
    if include_dj:
        dj_rate = get_dj_rate(client)
        dj_price = dj_rate * days * qty
        
        breakdown["dj_rate"] = dj_rate
        breakdown["dj_price"] = dj_price
        breakdown["total"] = base_price + dj_price
    
    return breakdown["total"], breakdown


def format_price_breakdown(breakdown: dict) -> str:
    """
    Makes a price breakdown easy to read.
    
    Args:
        breakdown: Dict from calculate_total_price()
        
    Returns:
        Nicely formatted multi-line string
        
    Example output:
        Equipment: $75.00/day × 3 days × 1 qty = $225.00
        DJ Service: $150.00/day × 3 days × 1 qty = $450.00
        Total: $675.00
    """
    lines = []
    
    # Equipment line
    lines.append(
        f"Equipment: ${breakdown['daily_rate']:.2f}/day × {breakdown['days']} days × "
        f"{breakdown['qty']} qty = ${breakdown['base_price']:.2f}"
    )
    
    # DJ line if they added it
    if breakdown['dj_price'] > 0:
        lines.append(
            f"DJ Service: ${breakdown['dj_rate']:.2f}/day × {breakdown['days']} days × "
            f"{breakdown['qty']} qty = ${breakdown['dj_price']:.2f}"
        )
    
    # Bottom line
    lines.append(f"Total: ${breakdown['total']:.2f}")
    
    return "\n".join(lines)