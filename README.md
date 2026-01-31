# Overview

SoundHire Cloud is a professional sound equipment rental management system designed to streamline the booking and inventory management process for audio equipment rental businesses. As a software engineer, I built this application to explore cloud database integration patterns, RESTful data operations, and real-world business logic implementation in a distributed system architecture.

The application is a Python command-line interface (CLI) that connects to a Supabase PostgreSQL database to manage rental packages, equipment inventory, and customer bookings. It provides complete CRUD (Create, Read, Update, Delete) functionality for managing sound equipment packages and demonstrates advanced database concepts including multi-table relationships, junction tables, and complex availability queries.

Key features include:

- **Package Management**: Browse and manage curated equipment packages (Basic, Standard, Premium)

- **Intelligent Availability Checking**: Validates rental availability by analyzing date range overlaps and stock levels
- **Dynamic Price Calculation**: Computes total rental costs based on duration, quantity, and optional DJ services
- **Booking System**: Complete reservation workflow with customer information and status tracking

This project helped me deepen my understanding of cloud database design, Python database interaction patterns, and building maintainable business logic layers that separate concerns effectively.

**Usage:**

**Usage:**

```bash

# List all available packages
python -m soundhire.cli list-packages

# View detailed package information
python -m soundhire.cli package-details --id 1

# Create a new booking
python -m soundhire.cli create-booking --package-id 1 --name "John Doe" \
  --phone "555-1234" --email "john@example.com" \
  --start 2025-11-15 --end 2025-11-17 --qty 1 --include-dj false

# List all bookings
python -m soundhire.cli list-bookings

# List all available packages
python -m soundhire.cli list-packages

# View detailed package information
python -m soundhire.cli package-details --id 1

# Create a new booking
python -m soundhire.cli create-booking --package-id 1 --name "John Doe" \
  --phone "555-1234" --email "john@example.com" \
  --start 2025-11-15 --end 2025-11-17 --qty 1 --include-dj false

# List all bookings
python -m soundhire.cli list-bookings
```

[Software Demo Video](https://youtu.be/uRE2pu3lv_k)

## Cloud Database

**Database Platform**: Supabase (PostgreSQL)

Supabase is an open-source Firebase alternative that provides a managed PostgreSQL database with a RESTful API, real-time subscriptions, and authentication. I chose Supabase because it offers a production-grade PostgreSQL database with excellent Python client libraries, making it ideal for learning cloud database integration patterns.

**Database Structure:**

The database schema consists of five interconnected tables demonstrating relational database design principles:

1. **`packages`** - Rental package catalog
   - Primary table storing package information (name, description, daily_rate, stock)
   - Represents the core offerings (Basic, Standard, Premium packages)

2. **`gear`** - Equipment inventory catalog
   - Stores individual equipment items (speakers, mixers, microphones, etc.)
   - Categorized by type with detailed specifications

3. **`package_gear`** - Junction table (many-to-many relationship)
   - Links packages to their included gear items
   - Stores quantity and configuration notes for each item in a package
   - Demonstrates normalized database design to avoid data redundancy

4. **`bookings`** - Customer reservations
   - Records rental transactions with customer contact information
   - Tracks date ranges, quantity, pricing, and status
   - Foreign key relationship to packages table
   - Includes constraints to ensure data integrity (valid date ranges, positive quantities)

5. **`settings`** - Application configuration
   - Stores global settings like DJ service daily rate
   - Single-row table pattern for configuration values

**Key Relationships:**

- One-to-many: `packages` → `bookings` (one package can have many bookings)

- Many-to-many: `packages` ↔ `gear` (through `package_gear` junction table)
- Referential integrity enforced through foreign keys with CASCADE and RESTRICT constraints

**Indexes:**

- `idx_bookings_package_dates`: Optimizes availability queries
- `idx_package_gear_package`: Speeds up package content lookups
- `idx_bookings_status`: Enables efficient status-based filtering

## Development Environment

**Development Tools:**

- **Visual Studio Code**: Primary code editor with Python extension
- **Supabase Dashboard**: Cloud database management and SQL editor
- **Git**: Version control and collaboration
- **Python 3.x**: Runtime environment
- **Virtual Environment (venv)**: Dependency isolation

**Programming Language & Libraries:**

**Python 3.8+** with the following key dependencies:

- **supabase-py (2.3.4)**: Official Supabase Python client for database operations
  - Provides intuitive API for SELECT, INSERT, UPDATE, DELETE operations
  - Handles authentication and connection management
  
- **python-dotenv (1.0.0)**: Environment variable management
  - Loads sensitive credentials from .env file
  - Keeps secrets out of source code

- **argparse**: Built-in Python module for CLI argument parsing
  - Creates professional command-line interface
  - Provides automatic help documentation

**Code Structure:**

- Modular architecture with separation of concerns
- `config.py`: Configuration and environment management
- `db.py`: Database connection handling
- `models.py`: Data access layer (CRUD operations)
- `availability.py`: Business logic layer
- `cli.py`: Presentation layer (user interface)

## Useful Websites

- [Supabase Documentation](https://supabase.com/docs) - Comprehensive guide to Supabase features and PostgreSQL setup
- [Supabase Python Client Documentation](https://supabase.com/docs/reference/python/introduction) - Official Python SDK reference
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) - SQL syntax and database design patterns
- [Python argparse Tutorial](https://docs.python.org/3/howto/argparse.html) - Building command-line interfaces
- [PostgreSQL Date/Time Functions](https://www.postgresql.org/docs/current/functions-datetime.html) - Working with date ranges and intervals
- [Python Type Hints Guide](https://docs.python.org/3/library/typing.html) - Modern Python type annotations

## Future Work

- **Web Interface**: Build a React or Flask web UI for easier booking management and package browsing
- **Authentication & Authorization**: Implement user accounts with role-based access control (admin vs. customer views)
- **Advanced Reporting**: Add analytics dashboard showing booking trends, revenue metrics, and equipment utilization
- **Email Notifications**: Integrate email service to send booking confirmations and reminders to customers
- **Payment Integration**: Connect to Stripe or similar payment gateway for online booking payments
- **Calendar Integration**: Visual calendar view showing equipment availability and booking schedules
- **Mobile App**: Native iOS/Android app for on-the-go booking management
- **Inventory Tracking**: Add maintenance schedules and equipment condition tracking
- **Multi-location Support**: Extend to support multiple warehouse locations with inventory transfers
- **Advanced Search**: Full-text search capabilities for finding packages by equipment type or feature
