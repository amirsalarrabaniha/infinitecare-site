# Infinite Care Beauty Clinic – website + Django backend

Redesigned, bilingual (EN/HU) website for https://www.infinitecare.hu, rebuilt with the original images and fonts
(Montserrat, Playfair Display, Mr Dafoe) and new animations. All content is managed in Django admin.

```
backend/            Django project (config/, content/ app = site content, contact/ app = messages, templates/site/)
css/ js/ assets/    design, animations, original images (served by Django as /static/…)
index.html …, hu/   static export of the site for GitHub Pages (generated from the DB)
```

## Run locally
```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # set SECRET_KEY, DEBUG=True for local
python manage.py migrate
python manage.py load_initial_content   # seeds all original texts, prices, images (EN+HU)
python manage.py createsuperuser
python manage.py runserver      # http://localhost:8000/en/ , /hu/ , /admin/
python manage.py test           # 20 tests (contact API, pages, JSON API, export)
```

## URLs
| URL | |
|---|---|
| `/en/`, `/en/services/`, `/en/prices/` (and `/hu/…`) | pages rendered from the DB |
| `/` | redirects to the remembered language (`ic-lang` cookie) or `/en/` |
| `/admin/` | Django admin: site settings, home page texts, counters, services, packages, price categories/items, contact messages (mark read/unread, delete) |
| `POST /api/contact/` | JSON `{name,email,phone,message,lang,website}` → 201 / 422 (validation) / 429 (rate limit). `website` is a honeypot. |
| `GET /api/settings/?lang=hu`, `/api/home/`, `/api/services/`, `/api/packages/`, `/api/prices/` | read-only JSON |

Language switcher: every page links to the same page in the other language (`/en/prices/` ↔ `/hu/prices/`,
`prices.html` ↔ `hu/prices.html` in the static copy). The choice is stored in `localStorage` + cookie; visiting the
site later from outside opens the remembered language. `<html lang>` and `hreflang` alternates are set.

## Environment (`backend/.env`, see `.env.example`)
`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, `SQLITE_PATH`, `MEDIA_ROOT`,
`CONTACT_RATE_LIMIT`, `CONTACT_RATE_WINDOW`, `TRUST_X_FORWARDED_FOR`, `NOTIFY_EMAIL`, `EMAIL_HOST`, `EMAIL_PORT`,
`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `DEFAULT_FROM_EMAIL`,
`STATIC_EXPORT_API_URL`, `STATIC_EXPORT_SITE_URL`. Without `NOTIFY_EMAIL`/`EMAIL_HOST` messages are only stored.

## Static GitHub Pages copy
```bash
cd backend && python manage.py export_static [--api-url https://your-backend/api/contact/]
```
Regenerates `index.html`, `services.html`, `prices.html`, `hu/*.html` and copies uploaded images to `assets/media/`.
Without an API URL the contact form opens the visitor's mail app (mailto). With one, add the Pages origin to `CORS_ALLOWED_ORIGINS`.

## Deploy
* **Render / Railway**: new Web Service from this repo. Build: `pip install -r backend/requirements.txt`.
  Start: see `Procfile` (migrate, seed if empty, collectstatic, gunicorn). Set the env vars above
  (`DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `TRUST_X_FORWARDED_FOR=True`). SQLite and uploads need a
  persistent disk: mount one (e.g. `/var/data`) and set `SQLITE_PATH=/var/data/db.sqlite3`, `MEDIA_ROOT=/var/data/media`.
  Create the admin with `python manage.py createsuperuser` in the service shell.
* **VPS**: clone, create venv, `.env`, migrate/seed/collectstatic, run `gunicorn config.wsgi -b 127.0.0.1:8000`
  under systemd behind nginx (TLS via certbot). nginx may serve `/media/` directly from `MEDIA_ROOT`.
