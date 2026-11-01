"""Load YAML registrations into the local Docker PostgreSQL database."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("Install the YAML reader first: python -m pip install PyYAML")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--replace", action="store_true", help="Replace current registrations")
    mode.add_argument("--check", action="store_true", help="Test the load, then roll it back")
    args = parser.parse_args()
    data = yaml.safe_load(args.file.read_text(encoding="utf-8"))
    columns = {
        "registration_code", "full_name", "email", "event_name", "ticket_type",
        "registered_at", "source",
    }
    if not isinstance(data, dict) or data.get("table") != "event_registrations":
        sys.exit("The YAML table must be event_registrations.")
    records = data.get("records")
    if not isinstance(records, list) or not records:
        sys.exit("The YAML must contain a nonempty records list.")
    for index, record in enumerate(records, 1):
        if not isinstance(record, dict) or set(record) != columns:
            sys.exit(f"Record {index} must contain exactly: {', '.join(sorted(columns))}")
        if any(value is not None and not isinstance(value, str) for value in record.values()):
            sys.exit(f"Record {index}: values must be text or null; quote date/time values.")
        if record["source"] is None:
            sys.exit(f"Record {index}: source cannot be null.")

    # Escape text as a SQL literal; table and column identifiers are fixed below.
    payload = json.dumps(records).replace("'", "''")
    finish = "COMMIT" if args.replace else "ROLLBACK"
    sql = f"""
BEGIN;
SET LOCAL standard_conforming_strings = on;
DELETE FROM public.event_registrations;
INSERT INTO public.event_registrations (
    registration_code, full_name, email, event_name, ticket_type, registered_at, source
)
SELECT registration_code, full_name, email, event_name, ticket_type, registered_at, source
FROM jsonb_to_recordset('{payload}'::jsonb) AS r(
    registration_code text, full_name text, email text, event_name text,
    ticket_type text, registered_at timestamptz, source text
);
SELECT COUNT(*) AS total_rows,
       COUNT(*) FILTER (WHERE full_name IS NULL OR btrim(full_name) = '') AS missing_names
FROM public.event_registrations;
{finish};
"""
    result = subprocess.run(
        ["docker", "compose", "exec", "-T", "database", "psql", "-U", "quality_user",
         "-d", "event_quality", "-v", "ON_ERROR_STOP=1"],
        input=sql, text=True, encoding="utf-8", cwd=Path(__file__).resolve().parent,
    )
    if result.returncode:
        sys.exit(result.returncode)
    print("Registrations replaced." if args.replace else "Check complete; data changes rolled back.")


if __name__ == "__main__":
    main()
