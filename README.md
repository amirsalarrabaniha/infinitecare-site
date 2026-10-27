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
python manage.py load_initial_content   # seeds all original texts, images (EN+HU)
python manage.py createsuperuser
python manage.py runserver      # http://localhost:8000/en/ , /hu/ , /admin/
python manage.py test           # contact API, pages, gallery, blog, JSON API, export
```

## URLs
| URL | |
|---|---|
| `/en/`, `/en/services/`, `/en/blog/` (and `/hu/…`) | pages rendered from the DB |
| `/en/blog/<slug>/`, `/hu/blog/<slug>/` | one blog post (same slug in both languages; unpublished posts return 404) |
| `/` | redirects to the remembered language (`ic-lang` cookie) or `/en/` |
| `/admin/` | Django admin: site settings, home page texts, counters, services, packages, **gallery photos, video clips, blog posts**, contact messages (mark read/unread, delete) |
| `POST /api/contact/` | JSON `{name,email,phone,message,lang,website}` → 201 / 422 (validation) / 429 (rate limit). `website` is a honeypot. |
| `GET /api/settings/?lang=hu`, `/api/home/`, `/api/services/`, `/api/packages/`, `/api/gallery/` (photos + videos), `/api/blog/`, `/api/blog/<slug>/` | read-only JSON |

Language switcher: every page links to the same page in the other language (`/en/services/` ↔ `/hu/services/`,
`services.html` ↔ `hu/services.html` in the static copy). The choice is stored in `localStorage` + cookie; visiting the
site later from outside opens the remembered language. `<html lang>` and `hreflang` alternates are set.

## Environment (`backend/.env`, see `.env.example`)
`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, `SQLITE_PATH`, `MEDIA_ROOT`,
`CONTACT_RATE_LIMIT`, `CONTACT_RATE_WINDOW`, `TRUST_X_FORWARDED_FOR`, `NOTIFY_EMAIL`, `EMAIL_HOST`, `EMAIL_PORT`,
`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `DEFAULT_FROM_EMAIL`,
`STATIC_EXPORT_API_URL`, `STATIC_EXPORT_SITE_URL`. Without `NOTIFY_EMAIL`/`EMAIL_HOST` messages are only stored.

## Clinic photos, videos and blog
* **Gallery + reels** (home page): admin → *Gallery photos* / *Video clips*. Photos have category (clinic / treatments / events), EN+HU caption (used as alt text), order and an *active* flag;
  the page shows filter buttons and a lightbox. Clips are short muted MP4s with a poster, played when scrolled into view (not with *reduce motion*).
  Source files live in `assets/images/gallery/` and `assets/video/` and are copied to the media folder by `load_initial_content`.
  **Existing databases** (seeded before this feature): `python manage.py load_clinic_media --update-images` adds the gallery, clips and starter blog posts and swaps in the clinic photos (without the flag the home/service images are left alone).
* **Blog**: admin → *Blog posts* (EN+HU title, summary and article, cover, date, *published* flag; HU falls back to EN when empty).
  Article text: blank line = new paragraph, `## Heading`, lines starting with `- ` = bullet list. The slug is shared by both languages.
  Three starter posts are seeded (first visit, laser hair removal prep/aftercare, teeth whitening basics). **They are draft copy – the clinic should review and edit them (admin) before relying on them.**
  Blog pages carry `<title>`, meta description (= summary), `hreflang`, canonical, Open Graph and `BlogPosting` JSON-LD. There is no sitemap in this project.
* The static export writes `blog.html`, `blog/<slug>.html` and the `hu/` equivalents (and removes posts that were unpublished); `wrangler.toml` needs no change
  (`html_handling = "auto-trailing-slash"` serves them at `/blog`, `/blog/<slug>`, `/hu/blog`, `/hu/blog/<slug>`).
* Gallery photos/videos show clinic clients – make sure the clinic has their consent.

## Static GitHub Pages copy
```bash
cd backend && python manage.py export_static [--api-url https://your-backend/api/contact/]
```
Regenerates `index.html`, `services.html`, `blog.html`, `blog/<slug>.html`, `hu/*.html`, `hu/blog/<slug>.html` and copies uploaded images to `assets/media/`.
Without an API URL the contact form opens the visitor's mail app (mailto). With one, add the Pages origin to `CORS_ALLOWED_ORIGINS`.

Also written by the export: `sitemap.xml` (with hreflang alternates), `robots.txt` and `llms.txt` (use `--site-url` so they and the
`<link rel="canonical">` tags carry the live origin; `--clean-urls` links to `/services` instead of `/services.html`, matching
`html_handling = "auto-trailing-slash"`). `assets/media/` is only added to, never wiped.

### Performance, accessibility and security notes
* **Fonts are self-hosted** (`assets/fonts/*.woff2`: Montserrat, Playfair Display and Mr Dafoe, SIL Open Font License; latin plus a
  latin-ext subset that covers Hungarian ő/ű). `style.css` has `font-display: swap` faces and metric-matched fallbacks to avoid layout
  shifts; no request goes to Google Fonts.
* **Images**: seed/uploaded photos are WebP. Templates add `width`/`height` through the `imgsize` filter
  (`content/templatetags/site_extras.py`, needs Pillow, silently skipped if it is missing), the LCP image has `fetchpriority="high"`,
  everything below the fold is `loading="lazy"`.
* **Google Maps** loads only after the visitor clicks "Show the map" (`data-map` facade in `index.html`/`main.js`).
* **`_headers`** (served by Workers static assets, so keep it out of `.assetsignore`): CSP, `nosniff`, Referrer-Policy,
  Permissions-Policy, HSTS, COOP and cache rules. `css/` and `js/` are linked with `?v=<content hash>` (see `asset_version()` in
  `content/views.py`) and cached for a year; photos/video for 30 days; HTML is revalidated. If you add a third-party script, font,
  frame or image host, add it to the CSP there. API responses come from the Worker, not from `_headers`.
* Check with `npx lighthouse@13 <url>` (the *Agentic browsing* category needs Lighthouse 13+). The contact form carries WebMCP
  declarative attributes (`toolname`, `tooldescription`, `toolparamdescription`).

## Deploy
* **Render / Railway**: new Web Service from this repo. Build: `pip install -r backend/requirements.txt`.
  Start: see `Procfile` (migrate, seed if empty, collectstatic, gunicorn). Set the env vars above
  (`DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `TRUST_X_FORWARDED_FOR=True`). SQLite and uploads need a
  persistent disk: mount one (e.g. `/var/data`) and set `SQLITE_PATH=/var/data/db.sqlite3`, `MEDIA_ROOT=/var/data/media`.
  Create the admin with `python manage.py createsuperuser` in the service shell.
* **VPS**: clone, create venv, `.env`, migrate/seed/collectstatic, run `gunicorn config.wsgi -b 127.0.0.1:8000`
  under systemd behind nginx (TLS via certbot). nginx may serve `/media/` directly from `MEDIA_ROOT`.

## Cloudflare Workers (live: https://infinitecare-site.amyrsalarr.workers.dev)
The Worker `infinitecare-site` serves the exported static EN/HU site as Workers static assets and implements
`POST /api/contact` itself (`cloudflare/worker.js`): same JSON contract, validation, honeypot and rate limit as Django.
Messages are stored in **D1** when a `DB` binding is configured (schema: `cloudflare/schema.sql`), otherwise in the
**Workers KV** namespace bound as `MESSAGES` (current setup). **Django admin does not run on Workers**; content edits are
made in the Django admin (locally or on a Python host) and published by re-exporting.

```bash
export CLOUDFLARE_API_TOKEN=…  CLOUDFLARE_ACCOUNT_ID=164584608fafa1395f843df7bb17e1c7   # Node.js >= 22
cd backend && python manage.py export_static --api-url /api/contact/ \
  --site-url https://infinitecare-site.amyrsalarr.workers.dev/ --clean-urls && cd ..
npx wrangler@latest deploy                    # uses wrangler.toml, uploads files not listed in .assetsignore
npx wrangler@latest kv key list --binding MESSAGES --remote          # list stored messages (keys msg:…)
npx wrangler@latest kv key get --binding MESSAGES --remote "msg:<id>" # read one message
```
Switch to D1 (needs an API token with *D1 Edit*): `npx wrangler d1 create infinitecare-messages`,
`npx wrangler d1 execute infinitecare-messages --remote --file cloudflare/schema.sql`, uncomment the
`[[d1_databases]]` block in `wrangler.toml`, deploy; query with `npx wrangler d1 execute infinitecare-messages --remote --command "SELECT * FROM contact_messages"`.

Why not full Django on Workers: Python Workers + `django-cf` (D1/R2) exist, but django-cf requires the Workers Paid plan
(Django start-up exceeds free CPU limits), D1 has no transactions and Django admin support is documented as limited.
The exported static site on Workers is the reliable option; Django stays deployable on Render/Railway/VPS.

## Cloudflare: Django backend (live: https://infinitecare-api.amyrsalarr.workers.dev)
The Worker `infinitecare-api` runs the full Django project on Cloudflare Python Workers. Persistence is a
**SQLite Durable Object** (`django_cf.db.backends.do`) — D1 is not used because the current API token lacks
*Account › D1 › Edit*, and R2 is not enabled on the account. Uploaded media go into the same Durable Object
via `cfmedia.storage.DatabaseStorage`; seeded images are served from static assets.

```bash
export CLOUDFLARE_API_TOKEN=… CLOUDFLARE_ACCOUNT_ID=164584608fafa1395f843df7bb17e1c7   # Node.js ≥ 22, uv
cd cf-django
uv sync
# first deploy: wrangler secret put SECRET_KEY  and  MGMT_TOKEN
uv run pywrangler deploy
# one-time setup (replace $MGMT_TOKEN):
curl -XPOST -H "X-Mgmt-Token: $MGMT_TOKEN" https://infinitecare-api.amyrsalarr.workers.dev/__manage__/migrate/
curl -XPOST -H "X-Mgmt-Token: $MGMT_TOKEN" https://infinitecare-api.amyrsalarr.workers.dev/__manage__/load_initial_content/
curl -XPOST -H "X-Mgmt-Token: $MGMT_TOKEN" -H 'content-type: application/json' \
  -d '{"username":"admin","email":"…","password":"…"}' \
  https://infinitecare-api.amyrsalarr.workers.dev/__manage__/superuser/
```
Admin: https://infinitecare-api.amyrsalarr.workers.dev/admin/
Site (DB-rendered): https://infinitecare-api.amyrsalarr.workers.dev/en/ and `/hu/`
The static Worker `infinitecare-site` posts its contact form to this Django `/api/contact/` (CORS allow-listed).

`_redirects` sends the retired `/prices` and `/hu/prices` URLs (the Prices page was removed) to `/services` and `/hu/services`.
