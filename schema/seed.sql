-- SoundHire Cloud Seed Data
-- Realistic sample data for testing and demonstration
-- Run this after schema.sql to populate the database

-- Insert gear catalog items
-- Categories: Speakers, Mixing, Microphones, Accessories
INSERT INTO gear (name, category, details) VALUES
    ('QSC K12.2 Active Speaker', 'Speakers', '2000W 12-inch powered loudspeaker, perfect for main PA'),
    ('JBL PRX818XLFW Subwoofer', 'Speakers', '18-inch powered subwoofer, 1500W, adds powerful low-end'),
    ('Yamaha MG16XU Mixer', 'Mixing', '16-channel analog mixer with USB and effects'),
    ('Behringer X32 Digital Mixer', 'Mixing', '32-channel digital mixer, professional-grade with remote control'),
    ('Shure SM58 Wired Microphone', 'Microphones', 'Industry-standard dynamic vocal microphone'),
    ('Shure BLX24/SM58 Wireless Mic', 'Microphones', 'Wireless handheld system with SM58 capsule'),
    ('Ultimate Support TS-80B Speaker Stand', 'Accessories', 'Tripod speaker stand, adjustable height'),
    ('Radial ProD2 Stereo DI Box', 'Accessories', 'Passive direct box for keyboards/laptops'),
    ('QSC CP8 Compact Speaker', 'Speakers', '1000W 8-inch powered speaker, great for monitors'),
    ('Sennheiser e835 Microphone', 'Microphones', 'Dynamic cardioid vocal mic, rugged construction');

-- Insert rental packages
-- Three tiers: Basic, Standard, Premium
INSERT INTO packages (name, description, daily_rate, stock) VALUES
    (
        'Basic Sound Package',
        'Perfect for small gatherings, presentations, or intimate events up to 50 people. Includes compact PA system with basic mixing capabilities.',
        75.00,
        3
    ),
    (
        'Standard Sound Package',
        'Ideal for weddings, corporate events, or parties up to 150 people. Professional-quality speakers with subwoofer and wireless microphones.',
        175.00,
        2
    ),
    (
        'Premium Sound Package',
        'Top-tier system for concerts, large events, or venues up to 300+ people. Digital mixing console with full wireless capabilities and monitor system.',
        350.00,
        1
    );

-- Link gear items to packages
-- Basic Package (ID 1): Small speakers, basic mixer, wired mic, stands
INSERT INTO package_gear (package_id, gear_id, qty, notes) VALUES
    (1, 9, 2, 'Two compact speakers for main output'),  -- QSC CP8
    (1, 3, 1, 'Simple analog mixer for basic mixing'),  -- Yamaha MG16XU
    (1, 5, 2, 'Two wired vocal microphones'),          -- Shure SM58
    (1, 7, 2, 'Speaker stands for proper positioning'), -- Ultimate Support stands
    (1, 8, 1, 'DI box for music playback');            -- Radial DI

-- Standard Package (ID 2): Full-range speakers, sub, wireless mics, good mixer
INSERT INTO package_gear (package_id, gear_id, qty, notes) VALUES
    (2, 1, 2, 'Two main PA speakers'),                  -- QSC K12.2
    (2, 2, 1, 'Powered subwoofer for bass'),            -- JBL sub
    (2, 3, 1, 'Professional mixing console'),           -- Yamaha mixer
    (2, 6, 2, 'Two wireless microphone systems'),       -- Shure wireless
    (2, 7, 2, 'Speaker stands'),                        -- stands
    (2, 8, 1, 'Stereo DI box'),                         -- DI
    (2, 9, 2, 'Additional monitors if needed');         -- CP8 monitors

-- Premium Package (ID 3): Top speakers, subs, digital mixer, wireless setup, monitors
INSERT INTO package_gear (package_id, gear_id, qty, notes) VALUES
    (3, 1, 4, 'Four main PA speakers for coverage'),    -- QSC K12.2
    (3, 2, 2, 'Dual subwoofers for powerful bass'),     -- JBL subs
    (3, 4, 1, 'Digital mixing console X32'),            -- Behringer X32
    (3, 6, 4, 'Four wireless microphone systems'),      -- Shure wireless
    (3, 10, 2, 'Additional vocal mics'),                -- Sennheiser
    (3, 7, 4, 'Speaker stands for all speakers'),       -- stands
    (3, 8, 2, 'Stereo DI boxes for multiple sources'),  -- DI
    (3, 9, 4, 'Four monitor speakers for stage');       -- CP8 monitors

-- Insert application settings
-- DJ daily rate that can be added to any package
INSERT INTO settings (id, dj_daily_rate) VALUES
    (1, 150.00);  -- Professional DJ service costs $150 per day

-- Insert sample bookings for testing
-- These demonstrate the booking system with various scenarios
INSERT INTO bookings (package_id, customer_name, phone, email, start_date, end_date, qty, include_dj, total_price, status) VALUES
    (
        1,
        'Akwero Sophia',
        '555-0101',
        'sarah.j@email.com',
        '2025-11-15',
        '2025-11-15',
        1,
        FALSE,
        75.00,  -- 1 day * $75 * 1 qty
        'confirmed'
    ),
    (
        2,
        'Akot Immaculate',
        '555-0202',
        'mchen@company.com',
        '2025-11-20',
        '2025-11-22',
        1,
        TRUE,
        975.00,  -- 3 days * ($175 + $150 DJ) * 1 qty
        'confirmed'
    ),
    (
        3,
        'Ayaa Rose',
        '555-0303',
        'emily.r@events.com',
        '2025-12-01',
        '2025-12-01',
        1,
        TRUE,
        500.00,  -- 1 day * ($350 + $150 DJ) * 1 qty
        'pending'
    );
    