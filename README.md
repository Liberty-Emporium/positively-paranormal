# Positively Paranormal 👻

A mobile-friendly paranormal investigation web toolkit. Record EVP, measure EMF, track motion, log evidence — all from your phone browser.

## Features

- **🎙️ EVP Recorder** — Record audio with waveform visualization, analyze for electronic voice phenomena
- **📡 EMF Meter** — Use phone's magnetometer/compass to detect electromagnetic fluctuations
- **📱 Motion Detection** — Accelerometer-based movement triggers
- **📷 Evidence Logging** — Upload photos, videos, audio, documents
- **📋 Case Management** — Full investigation case files with sessions, notes, classification
- **🔐 Investigator Accounts** — Secure multi-user with registration
- **📱 PWA Ready** — Works offline, installable on phone home screen

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Tech Stack

- **Backend:** Django 6.1
- **Database:** SQLite (dev), PostgreSQL-ready
- **Frontend:** Vanilla JS, CSS custom properties
- **Sensors:** Web Audio API, DeviceOrientation API, Generic Sensor API
- **PWA:** Web App Manifest

## License

MIT

---

## Deployment Log

### 2026-08-19 — Initial Deploy to Contabo VPS

The app was deployed to **paranormal.jays-web.org** on a Contabo VPS at `169.58.78.73`.

**Stack:**
- **Nginx** — reverse proxy, serves static files, SSL termination
- **Gunicorn** — WSGI server via systemd service (`positively-paranormal`)
- **Systemd** — auto-start gunicorn on boot
- **Cloudflare** — DNS proxying, edge SSL
- **Let's Encrypt (pending)** — origin SSL once DNS record propagates; currently using self-signed origin cert with Cloudflare Full mode

**Setup Steps:**
1. Created Django project with `investigator` and `accounts` apps
2. Built data models: `Case`, `InvestigationSession`, `EVPSession`, `EMFReading`, `Evidence`, `MotionEvent`
3. Built mobile-first dark UI with EVP recorder (Web Audio API) and EMF meter (DeviceOrientation / Magnetometer API)
4. Pushed source to GitHub: `Liberty-Emporium/positively-paranormal`
5. Rsynced project to `/var/www/positively-paranormal/` on VPS
6. Python venv + pip installs + migrations + superuser created
7. Gunicorn systemd service configured on `pp.sock`
8. Nginx sites-available/sites-enabled config for `paranormal.jays-web.org`
9. Self-signed SSL cert for origin; Cloudflare set to Full mode
10. DNS A record added: `paranormal` → `169.58.78.73` (proxied)

**Bugs Fixed During Deploy:**
- URL namespace mismatch — templates used `{% url 'dashboard' %}` instead of `{% url 'investigator:dashboard' %}` (and all other investigator URLs). Fixed by adding `investigator:` prefix throughout templates and settings.
- Nginx 400 error — `proxy_params` include was setting `$http_host` incorrectly. Replaced with explicit proxy headers.
- Missing HTTPS server block — initial config only had `listen 80`. Added `listen 443 ssl` with self-signed cert.
- `LOGIN_REDIRECT_URL` was `'dashboard'` instead of `'investigator:dashboard'`.

**Admin Credentials:**
- URL: `https://paranormal.jays-web.org/admin/`
- User: `admin`
- Pass: `paranormal2026`