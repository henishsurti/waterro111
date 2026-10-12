# Nirmal Agency Manager V9.1

- Rebranded from AquaFlow to **Nirmal Agency** (new logo, favicon, company name, job-card header, backup file name).
- New analytics dashboard: period selector with previous-period comparison, alert strip, performance and operations KPIs, revenue / jobs / AMC-renewal charts, status donut, service-type and area mix, technician performance, upcoming work, top customers and recent activity. Everything is clickable and opens a filtered list or drill-down.
- Live database: `/api/changes` revision polling, automatic refresh, "Live database" badge, manual Refresh, and optimistic-concurrency (`base_revision`, HTTP 409) so simultaneous editors cannot overwrite each other.
- List screens (Services, Customers, AMC, RO) accept dashboard filters and show removable filter chips.
- Security: the web server now serves only `index.html` and `assets/`; previously `aquaflow.db` (with password hashes) and the backend code were downloadable.
- Fixes: server settings returned as text broke login in server mode; CSV export wrote a single line; multi-line "parts used" input was not parsed; an unsaved change made during a sync could be lost; save indicator threw an error after sync.

# AquaFlow Professional V9

- Added FastAPI backend with session authentication and CSRF protection.
- Added relational API sync with transactional SQLite persistence.
- Added server bootstrap and audit endpoint.
- Added local-first fallback when the API is unavailable.
- Added server/local connection indicator.
- Added keyboard and reduced-motion accessibility improvements.
- Added stronger mobile touch targets and modal ergonomics.
- Added deployment, QA and security documentation.
- Preserved AquaFlow V8 business workflows and UI while introducing a full-stack delivery path.
