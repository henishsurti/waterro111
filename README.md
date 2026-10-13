# Nirmal Agency — RO Service & AMC Manager (V9.1)

Nirmal Agency Manager is a professional web application for RO purifier service businesses covering customer records, RO assets, AMC contracts, service scheduling, technician dispatch, field execution, billing, notifications, reports and auditability.

## Included layers
- **Product/UI/UX:** responsive admin workspace, mobile technician workflow, design tokens, keyboard navigation, dark/light mode, touch targets and accessible focus states.
- **Frontend:** V8 business workflows retained and hardened with V9 API bridge, validation, local-first fallback, backup/restore and diagnostics.
- **Backend:** FastAPI, secure session cookie, CSRF token, authenticated bootstrap/sync, audit logging and relationship validation.
- **Database:** normalized SQLite relational schema with foreign keys, indexes, service parts/photos, audit log and application snapshot metadata.
- **QA/Delivery:** smoke/API tests, QA test plan, deployment guide, Dockerfile, compose file and Windows one-click launcher.

## Live dashboard
- Every KPI card, chart bar, donut slice, technician row and activity item is clickable and opens a pre-filtered list or a drill-down.
- Date ranges (7 days / 30 days / 90 days / 12 months) with comparison against the previous period: revenue, jobs completed, collection rate, turnaround, on-time %, new customers.
- Live data: while the server is running the browser checks `/api/changes` every 10 seconds and reloads automatically when anyone changes data; the **Live database** badge shows the last update. If two people edit at once the second save is rejected (HTTP 409) and the latest data is loaded instead of silently overwriting.
- Export the dashboard figures to CSV from the dashboard header.

## Local run
### Full-stack (recommended)
Double-click `start-professional.bat`, then open `http://127.0.0.1:8799`. Data is stored in `aquaflow.db` (SQLite) and shared by every signed-in user.

### Frontend-only fallback
Open `index.html` or run `py -m http.server 8799`. Local browser storage remains available if the API is not running.

## Demo
- Admin: `admin / admin123`
- Technician: `suresh / tech123`
- Technician: `iqbal / tech123`

Demo credentials must be changed before any real deployment.

## Production
To run it live on your own server with HTTPS, a shared live database and daily backups, follow **[DEPLOY-VPS.md](DEPLOY-VPS.md)**.

Use PostgreSQL, HTTPS, a long secret, Argon2id/bcrypt, strict RBAC, object storage for photos, backups, monitoring, rate limiting and a reverse proxy. See `DEPLOYMENT.md`.

## Files
- `index.html` — frontend
- `assets/` — Nirmal Agency logo and favicon
- `backend/app.py` — API
- `backend/requirements.txt` — backend dependencies
- `backend/tests/` — API tests
- `aquaflow.db` — reference database
- `database.sql` — relational schema
- `start-professional.bat` — Windows launcher
- `Dockerfile` / `docker-compose.yml` — container deployment
- `QA-TEST-PLAN.md` — QA checklist
- `DEPLOYMENT.md` — deployment/security
