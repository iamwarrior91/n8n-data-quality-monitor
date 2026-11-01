CREATE TABLE event_registrations (
    id BIGSERIAL PRIMARY KEY,
    registration_code TEXT,
    full_name TEXT,
    email TEXT,
    event_name TEXT,
    ticket_type TEXT,
    registered_at TIMESTAMPTZ,
    source TEXT NOT NULL
);

INSERT INTO event_registrations (
    registration_code,
    full_name,
    email,
    event_name,
    ticket_type,
    registered_at,
    source
) VALUES
    ('EVT-1001', 'Aisha Rahman', 'aisha@example.com', 'Product Summit 2026', 'Standard', NOW(), 'seed'),
    ('EVT-1002', 'Ben Lim', 'ben@example.com', 'Product Summit 2026', 'VIP', NOW(), 'seed'),
    ('EVT-1003', 'Carla Tan', 'carla@example.com', 'Product Summit 2026', 'Standard', NOW(), 'seed'),
    ('EVT-1004', 'Daniel Ong', 'daniel@example.com', 'Product Summit 2026', 'Standard', NOW(), 'seed'),
    ('EVT-1005', 'Elaine Goh', 'elaine@example.com', 'Product Summit 2026', 'VIP', NOW(), 'seed');
