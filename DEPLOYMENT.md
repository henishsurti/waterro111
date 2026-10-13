# Nirmal Agency Manager V9.1 — delivery & deployment

**Going live on a server? Follow [DEPLOY-VPS.md](DEPLOY-VPS.md)** (Docker, automatic HTTPS, daily backups).

## Local
1. Install Python 3.12+ / 3.13.
2. Run `start-professional.bat`.
3. Open `http://127.0.0.1:8799`.

## API
- Health: `/api/health`
- Swagger: `/api/docs`
- Login: `/api/auth/login`
- Session: `/api/auth/me`
- Bootstrap: `/api/bootstrap`
- Sync: `/api/sync`
- Audit: `/api/audit` (admin)

## Security before production
- Set `AQUAFLOW_ENV=production` (the compose file does): the server then refuses to start without a strong first-admin password and the demo logins/sample data are hidden.
- Set `AQUAFLOW_COOKIE_SECURE=1` behind HTTPS.
- Use PostgreSQL for multi-user production workloads.
- Never deploy `aquaflow.db` (demo data); a production database starts empty.
- Use Argon2id or bcrypt through a maintained password library.
- HTTPS reverse proxy (Caddy) and login rate limiting are built in; add log monitoring.
- Move service photos to object storage.
- Daily backups are built in (`backend/backup.py`); copy them off the server and practise a restore.
- Restrict CORS to exact production origins.
- Technicians can only update their own jobs (enforced on the server); finer-grained admin roles are not implemented.

## Testing
Run `python -m pytest backend/tests -q` after installing requirements and pytest.

## Architecture
Browser UI -> FastAPI -> SQLite (local reference) / PostgreSQL (production).
The UI retains a local-first fallback for offline use; when the API is available, successful login loads relational server state and writes changes through the sync endpoint.
