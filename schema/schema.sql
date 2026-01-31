-- SoundHire Cloud Database Schema
-- PostgreSQL/Supabase DDL for sound equipment rental management
-- This schema supports multiple related tables as required by the Cloud Database module

-- Table: packages
-- Stores rental packages (Basic, Standard, Premium, etc.)
CREATE TABLE packages (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    daily_rate NUMERIC(12,2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: gear
-- Catalog of individual equipment items (speakers, mixers, mics, etc.)
CREATE TABLE gear (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    details TEXT
);

-- Table: package_gear
-- Junction table linking packages to their included gear items
-- Demonstrates many-to-many relationship required for the module
CREATE TABLE package_gear (
    id BIGSERIAL PRIMARY KEY,
    package_id BIGINT NOT NULL REFERENCES packages(id) ON DELETE CASCADE,
    gear_id BIGINT NOT NULL REFERENCES gear(id) ON DELETE RESTRICT,
    qty INTEGER NOT NULL DEFAULT 1,
    notes TEXT
);

-- Table: settings
-- Application-wide settings (currently stores DJ daily rate)
-- Constrained to a single row for configuration values
CREATE TABLE settings (
    id SMALLINT PRIMARY KEY DEFAULT 1,
    dj_daily_rate NUMERIC(12,2) NOT NULL,
    CONSTRAINT single_row CHECK (id = 1)
);

-- Table: bookings
-- Customer rental reservations with date ranges and pricing
CREATE TABLE bookings (
    id BIGSERIAL PRIMARY KEY,
    package_id BIGINT NOT NULL REFERENCES packages(id) ON DELETE RESTRICT,
    customer_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    qty INTEGER NOT NULL,
    include_dj BOOLEAN NOT NULL DEFAULT FALSE,
    total_price NUMERIC(12,2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_date_range CHECK (end_date >= start_date),
    CONSTRAINT positive_qty CHECK (qty > 0)
);

-- Indexes for performance optimization
-- Critical for availability queries that filter by package and date ranges
CREATE INDEX idx_bookings_package_dates ON bookings(package_id, start_date, end_date);
CREATE INDEX idx_package_gear_package ON package_gear(package_id);
CREATE INDEX idx_bookings_status ON bookings(status);