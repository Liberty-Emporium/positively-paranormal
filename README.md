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