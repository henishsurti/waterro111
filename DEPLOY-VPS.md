# Going live on your own server (VPS)

This puts Nirmal Agency on a public HTTPS address with a real database that every user shares live.
You need about 30 minutes, a server and a domain name.

## What you need
- A small Linux VPS (Ubuntu 22.04 or 24.04, 1 GB RAM is enough) with ports **80** and **443** open.
- A domain or subdomain, for example `app.yourcompany.in`.

## One-time setup
1. **Point DNS at the server.** Create an `A` record for your domain pointing to the server's IP address. Wait until it resolves.
2. **Install Docker** on the server: `curl -fsSL https://get.docker.com | sh`
3. **Get the code:**
   ```
   git clone https://github.com/henishsurti/waterro111.git
   cd waterro111
   ```
4. **Configure:**
   ```
   cp .env.example .env
   nano .env
   ```
   Set `DOMAIN` and a strong `ADMIN_PASSWORD` (at least 10 characters). Optionally change `ADMIN_USER`.
5. **Start it:**
   ```
   docker compose up -d --build
   ```
6. **Check it:** `docker compose ps` should show `app` as *healthy*. Open `https://your-domain`, sign in as the admin, and you are live.
   The HTTPS certificate is obtained automatically the first time (it can take a minute).

The database starts **empty**: no demo customers and no demo logins. Add your technicians first (Technicians → Add; this also creates their phone login), then customers, RO machines and AMCs.

## Everyday use
- **Update to a new version:** `git pull && docker compose up -d --build` (data is kept).
- **Logs:** `docker compose logs -f app`
- **Stop / start:** `docker compose stop` / `docker compose start`
- **Forgot the admin password:**
  ```
  docker compose exec app python -c "import app,sys; c=app.conn(); c.execute('UPDATE users SET password_hash=? WHERE username=?',(app.hash_password(sys.argv[1]),sys.argv[2])); c.commit()" 'NewStrongPassword1' admin
  ```

## Backups (important)
A backup of the database is written automatically every 24 hours to the `backups/` folder next to `docker-compose.yml`, keeping the newest 30. Each one is checked for corruption when written.

**A backup on the same server is not enough** — if the server is lost, so are the backups. Copy them somewhere else regularly, for example from your own computer:
```
scp -r user@your-server:~/waterro111/backups ./nirmal-backups
```

**Restore a backup:**
```
docker compose stop app backup
docker compose run --rm --no-deps -v "$PWD/backups:/backups" --user 0 --entrypoint sh app -c "cp /backups/aquaflow-YYYYMMDD-HHMMSS.db /app/data/aquaflow.db && chown app /app/data/aquaflow.db"
docker compose start app backup
```

## Good to know
- **Security:** the app limits repeated wrong passwords, only lets technicians change their own jobs, and never serves the database or code. Keep the server updated (`apt update && apt upgrade`) and allow only SSH, 80 and 443 in the firewall.
- **One server only:** sign-in sessions are kept in memory, so restarting the app signs everyone out (their data is not lost).
- **Job photos:** before/after photos and signatures taken on a technician's phone are not yet stored on the server database. Work done, parts, charges and payment details are.
