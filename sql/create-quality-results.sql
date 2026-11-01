CREATE TABLE IF NOT EXISTS data_quality_results (
    id BIGSERIAL PRIMARY KEY,
    checked_at TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PASS', 'FAIL')),
    total_rows BIGINT NOT NULL,
    missing_names BIGINT NOT NULL,
    missing_emails BIGINT NOT NULL,
    missing_events BIGINT NOT NULL,
    missing_ticket_types BIGINT NOT NULL,
    missing_registration_dates BIGINT NOT NULL,
    duplicate_registration_codes BIGINT NOT NULL,
    message TEXT NOT NULL
);
