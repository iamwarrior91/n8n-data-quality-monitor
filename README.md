# Event Registration Data Quality Monitor

An n8n automation project that profiles event-registration data in PostgreSQL, identifies quality issues, and records a failed workflow execution when an issue is found.

## What It Checks

- Missing names, emails, event names, ticket types, and registration dates
- Duplicate registration codes
- Empty source data

## Workflow

```text
Manual trigger or daily schedule -> PostgreSQL data profile -> JavaScript evaluation -> Save results to PostgreSQL -> PASS or data-quality alert
```

The workflow runs every day at 9:00 AM after you activate it in n8n. It can also be executed manually while testing.

## Tools Used

- n8n
- Docker Compose
- PostgreSQL
- SQL
- JavaScript
- Git and GitHub

## Setup

1. Copy the environment template and choose private values:

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. Put the generated value in `N8N_ENCRYPTION_KEY` inside `.env`.

3. Start the project:

```powershell
docker compose up -d
```

4. Open `http://localhost:5678` and create your local n8n owner account.

5. Import `workflows/event-data-quality-monitor.json` in n8n.

6. In the **Profile event data** node, create PostgreSQL credentials:

```text
Host: database
Port: 5432
Database: event_quality
User: quality_user
Password: the POSTGRES_PASSWORD value in .env
```

7. Click **Execute workflow**. The seeded data should produce a successful execution. Activate the workflow when you are ready for the daily schedule.

## Demonstrate a Failed Check

Insert an intentionally bad record:

```powershell
docker compose exec database psql -U quality_user -d event_quality -c "INSERT INTO event_registrations (registration_code, full_name, email, event_name, ticket_type, registered_at, source) VALUES ('EVT-1001', NULL, 'test@example.com', 'Product Summit 2026', 'Standard', NOW(), 'test');"
```

Run the workflow again. It should fail and identify a missing name and duplicate registration code. Remove the test record afterward:

```powershell
docker compose exec database psql -U quality_user -d event_quality -c "DELETE FROM event_registrations WHERE source = 'test';"
```

## Future Improvements

- Send failures to email, Slack, or Discord
- Store quality-check history in a reporting table
- Add thresholds for acceptable missing-value rates
- Create a Power BI dashboard for data-quality trends

## Power BI results history

Every completed evaluation is saved to `public.data_quality_results` before the
PASS/FAIL branch. An intentional quality failure therefore remains available for reporting.
Connection/query failures before the save step are not recorded in this table.

For an existing database, apply the additional schema once (safe to repeat):

```powershell
Get-Content -Raw sql/create-quality-results.sql | docker compose exec -T database psql -U quality_user -d event_quality -v ON_ERROR_STOP=1
docker compose up -d
```

Reimport the updated workflow JSON into a new workflow, select your existing
PostgreSQL credential in both PostgreSQL nodes, and test it manually. Keep only
one scheduled workflow published. The insert returns the saved fields to the IF node.

Power BI Desktop: Get Data > PostgreSQL database. Use:

- Server: `localhost:5434`
- Database: `event_quality`
- Data connectivity: Import
- Database username: `quality_user`
- Password: your `.env` database password
- Table: `public.data_quality_results`

The database port is bound only to this computer. n8n continues to use
`database:5432` internally. Use Refresh in Power BI Desktop after workflow runs.
A published Power BI report accessing this local database needs an on-premises
data gateway for scheduled refresh, with the PC and database running.

Start with cards for latest status and total checks, and charts for checks by
status, missing-value counts, and results over time. Keep the database password
out of reports and version control.
