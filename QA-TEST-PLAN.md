# Nirmal Agency Manager V9.1 QA Test Plan

## Smoke
- [ ] App loads with no console errors.
- [ ] Admin login succeeds.
- [ ] Technician login succeeds.
- [ ] Invalid credentials are rejected.
- [ ] Logout clears the session.
- [ ] Server/local mode indicator is accurate.

## Customers
- [ ] Create customer.
- [ ] Edit customer.
- [ ] Mark active/inactive.
- [ ] Delete customer with confirmation.
- [ ] Invalid phone/email/date values are blocked.

## RO
- [ ] Create/edit/delete RO.
- [ ] RO cannot reference a missing customer.
- [ ] Service form filters RO by customer.

## AMC
- [ ] Create/edit/delete AMC.
- [ ] AMC dates and amount validate.
- [ ] Expiry is visible in dashboard/notifications.

## Services
- [ ] Create service and assign active technician.
- [ ] Technician sees assigned work only.
- [ ] Start -> in progress -> complete workflow works.
- [ ] Parts/labour/discount totals are correct.
- [ ] Before/after photos can be captured on supported browsers.
- [ ] Completion updates RO service dates and AMC usage.

## Data
- [ ] Export JSON.
- [ ] Restore JSON.
- [ ] Diagnostics report no broken references.
- [ ] API sync rejects broken relationships.
- [ ] SQLite foreign key integrity check returns `ok`.

## Responsive/accessibility
- [ ] 360px phone width.
- [ ] 768px tablet.
- [ ] 1366px desktop.
- [ ] Keyboard focus visible.
- [ ] Escape closes dialogs.
- [ ] Reduced-motion preference respected.

## Dashboard & live data (V9.1)
- Click every KPI card: it opens the matching list with a removable filter chip; "Clear all" restores the full list.
- Click a revenue / jobs bar: a drill-down lists the payments or jobs behind it; clicking a row opens the record.
- Click a donut slice or legend item, a service-type bar, an area bar, an AMC month bar, a technician row and a recent-activity row.
- Switch 7 / 30 / 90 days / 12 months and confirm the figures and the previous-period comparison change.
- Open the app on two devices: add a service on one; the other updates within ~10 seconds without reloading.
- Edit the same record on both devices: the second save shows "Another user changed the data" and loads the latest data.
- Stop the server: the badge changes to "Offline"; restart it and changes made offline are pushed or reconciled.
- Confirm `/aquaflow.db`, `/backend/app.py` and `/database.sql` return 404.
