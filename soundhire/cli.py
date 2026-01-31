"""
Command-line interface for SoundHire Cloud.

Provides commands for managing rental packages and bookings, all backed
by our Supabase PostgreSQL database.

Commands:
- list-packages: Browse available packages
- package-details: Get full details on a specific package
- create-booking: Make a new reservation
- list-bookings: See all current bookings

Usage:
    python -m soundhire.cli <command> [options]
"""

import sys
import argparse
from typing import NoReturn
from .config import load_environment
from .db import get_supabase_client
from . import models
from . import availability


def format_currency(amount: float) -> str:
    """Formats a number as USD currency."""
    return f"${amount:.2f}"


def command_list_packages(args) -> None:
    """
    Shows all our rental packages with what's included.
    """
    print("\n" + "="*80)
    print("SOUNDHIRE CLOUD - AVAILABLE PACKAGES")
    print("="*80 + "\n")
    
    try:
        client = get_supabase_client()
        packages = models.list_packages(client)
        
        if not packages:
            print("No packages found in the database.")
            return
        
        for pkg in packages:
            # Get package with gear contents
            full_pkg = models.get_package_with_contents(pkg["id"], client)
            
            print(f"📦 {full_pkg['name']} (ID: {full_pkg['id']})")
            print(f"   Daily Rate: {format_currency(full_pkg['daily_rate'])}")
            print(f"   Stock Available: {full_pkg['stock']}")
            
            if full_pkg.get("description"):
                print(f"   Description: {full_pkg['description']}")
            
            # Show included gear summary
            gear_items = full_pkg.get("gear_items", [])
            if gear_items:
                print(f"   Included Gear ({len(gear_items)} items):")
                for item in gear_items:
                    gear = item.get("gear", {})
                    qty = item.get("qty", 1)
                    gear_name = gear.get("name", "Unknown")
                    print(f"      • {qty}× {gear_name}")
            
            print()  # Blank line between packages
        
        print(f"Total packages: {len(packages)}\n")
        
    except Exception as e:
        print(f"❌ Error listing packages: {str(e)}", file=sys.stderr)
        sys.exit(1)


def command_package_details(args) -> None:
    """
    Shows everything about a specific package - full gear list and all.
    """
    package_id = args.id
    
    print("\n" + "="*80)
    print(f"PACKAGE DETAILS - ID {package_id}")
    print("="*80 + "\n")
    
    try:
        client = get_supabase_client()
        package = models.get_package_with_contents(package_id, client)
        
        if not package:
            print(f"❌ Package with ID {package_id} not found.")
            sys.exit(1)
        
        # Basic package info
        print(f"Name: {package['name']}")
        print(f"Daily Rate: {format_currency(package['daily_rate'])}")
        print(f"Stock: {package['stock']} available")
        print(f"Created: {package.get('created_at', 'N/A')}")
        
        if package.get("description"):
            print(f"\nDescription:\n{package['description']}")
        
        # Detailed gear list
        gear_items = package.get("gear_items", [])
        if gear_items:
            print(f"\n{'─'*80}")
            print("INCLUDED GEAR:")
            print(f"{'─'*80}\n")
            
            for item in gear_items:
                gear = item.get("gear", {})
                qty = item.get("qty", 1)
                notes = item.get("notes", "")
                
                print(f"• {gear.get('name', 'Unknown')} (Qty: {qty})")
                print(f"  Category: {gear.get('category', 'N/A')}")
                
                if gear.get("details"):
                    print(f"  Details: {gear['details']}")
                
                if notes:
                    print(f"  Notes: {notes}")
                
                print()  # Blank line between items
        else:
            print("\nNo gear items configured for this package.")
        
        print()
        
    except Exception as e:
        print(f"❌ Error retrieving package details: {str(e)}", file=sys.stderr)
        sys.exit(1)


def command_create_booking(args) -> None:
    """
    Creates a new rental booking.
    
    Checks availability first, calculates the price, then creates
    the booking if everything looks good.
    """
    print("\n" + "="*80)
    print("CREATE NEW BOOKING")
    print("="*80 + "\n")
    
    try:
        client = get_supabase_client()
        
        # Make sure the package exists
        pkg_response = client.table("packages").select("name").eq("id", args.package_id).execute()
        if not pkg_response.data:
            print(f"❌ Package ID {args.package_id} not found.")
            sys.exit(1)
        
        package_name = pkg_response.data[0]["name"]
        
        # Show what they're trying to book
        print(f"Package: {package_name} (ID: {args.package_id})")
        print(f"Customer: {args.name}")
        print(f"Contact: {args.phone} | {args.email}")
        print(f"Dates: {args.start} to {args.end}")
        print(f"Quantity: {args.qty}")
        print(f"DJ Service: {'Yes' if args.include_dj else 'No'}")
        print()
        
        # Check if we have it available
        print("Checking availability...")
        available, message = availability.is_package_available(
            args.package_id,
            args.start,
            args.end,
            args.qty,
            client
        )
        
        print(f"✓ {message}\n")
        
        if not available:
            print("❌ Can't make this booking - not enough availability.")
            sys.exit(1)
        
        # Work out the price
        print("Calculating price...")
        total_price, breakdown = availability.calculate_total_price(
            args.package_id,
            args.start,
            args.end,
            args.qty,
            args.include_dj,
            client
        )
        
        print(availability.format_price_breakdown(breakdown))
        print()
        
        # Save it to the database
        print("Creating booking...")
        booking = models.create_booking(
            package_id=args.package_id,
            customer_name=args.name,
            phone=args.phone,
            email=args.email,
            start_date=args.start,
            end_date=args.end,
            qty=args.qty,
            include_dj=args.include_dj,
            total_price=total_price,
            client=client
        )
        
        print(f"✅ Booking created successfully!")
        print(f"   Booking ID: {booking['id']}")
        print(f"   Status: {booking['status']}")
        print(f"   Total Price: {format_currency(total_price)}")
        print()
        
    except ValueError as e:
        print(f"❌ Validation error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error creating booking: {str(e)}", file=sys.stderr)
        sys.exit(1)


def command_list_bookings(args) -> None:
    """
    Shows all bookings we have in the system.
    """
    print("\n" + "="*80)
    print("ALL BOOKINGS")
    print("="*80 + "\n")
    
    try:
        client = get_supabase_client()
        bookings = models.list_bookings(client)
        
        if not bookings:
            print("No bookings found in the database.")
            return
        
        for booking in bookings:
            # Pull out the package name
            package_name = "Unknown"
            if booking.get("packages"):
                package_name = booking["packages"].get("name", "Unknown")
            
            # Display the booking info
            print(f"🎫 Booking #{booking['id']} - {booking['status'].upper()}")
            print(f"   Customer: {booking['customer_name']}")
            print(f"   Contact: {booking['phone']} | {booking['email']}")
            print(f"   Package: {package_name}")
            print(f"   Dates: {booking['start_date']} to {booking['end_date']}")
            print(f"   Quantity: {booking['qty']}")
            
            if booking.get('include_dj'):
                print(f"   DJ Included: Yes")
            
            print(f"   Total Price: {format_currency(booking['total_price'])}")
            print(f"   Created: {booking.get('created_at', 'N/A')}")
            print()
        
        print(f"Total bookings: {len(bookings)}\n")
        
    except Exception as e:
        print(f"❌ Error listing bookings: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main() -> NoReturn:
    """
    Main entry point - handles command parsing and routing.
    """
    # Load our environment variables
    load_environment()
    
    # Set up the command parser
    parser = argparse.ArgumentParser(
        description="SoundHire Cloud - Sound Equipment Rental Management",
        epilog="Check README.md for more info"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # list-packages command
    subparsers.add_parser(
        "list-packages",
        help="Show all rental packages"
    )
    
    # package-details command
    details_parser = subparsers.add_parser(
        "package-details",
        help="Get full details on a specific package"
    )
    details_parser.add_argument(
        "--id",
        type=int,
        required=True,
        help="Which package to look up"
    )
    
    # create-booking command
    booking_parser = subparsers.add_parser(
        "create-booking",
        help="Make a new booking"
    )
    booking_parser.add_argument("--package-id", type=int, required=True, help="Package to rent")
    booking_parser.add_argument("--name", type=str, required=True, help="Customer name")
    booking_parser.add_argument("--phone", type=str, required=True, help="Phone number")
    booking_parser.add_argument("--email", type=str, required=True, help="Email address")
    booking_parser.add_argument("--start", type=str, required=True, help="Start date (YYYY-MM-DD)")
    booking_parser.add_argument("--end", type=str, required=True, help="End date (YYYY-MM-DD)")
    booking_parser.add_argument("--qty", type=int, required=True, help="How many packages")
    booking_parser.add_argument(
        "--include-dj",
        type=lambda x: x.lower() in ['true', '1', 'yes', 'y'],
        required=True,
        help="Add DJ service? (true/false)"
    )
    
    # list-bookings command
    subparsers.add_parser(
        "list-bookings",
        help="Show all bookings"
    )
    
    # Parse and route
    args = parser.parse_args()
    
    # Send to the right command handler
    if args.command == "list-packages":
        command_list_packages(args)
    elif args.command == "package-details":
        command_package_details(args)
    elif args.command == "create-booking":
        command_create_booking(args)
    elif args.command == "list-bookings":
        command_list_bookings(args)
    else:
        parser.print_help()
        sys.exit(1)
    
    sys.exit(0)


# Entry point when running: python -m soundhire.cli
if __name__ == "__main__":
    main()