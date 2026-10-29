# Infinite Care – Next.js on Cloudflare Workers

Bilingual (EN/HU) website for [www.infinitecare.hu](https://www.infinitecare.hu), ported from the static Django export to a **vinext** (Next.js App Router on Vite) app that runs on Cloudflare Workers.

Blog posts and other CMS content are fetched from the existing Django API at request time (with a ~3 minute revalidate), so admin edits show up without a static rebuild. HTML is server-rendered for SEO.

This Worker is **`infinitecare-next`**. It does **not** replace the production static Worker `infinitecare-site`. DNS is unchanged until cutover.

## Why vinext (not OpenNext)

Cloudflare’s current recommendation for new Next.js apps on Workers is [vinext](https://github.com/cloudflare/vinext): native workerd local/dev, Vite HMR, App Router + RSC, and ISR via Workers Cache. OpenNext remains valid for existing apps; this is a greenfield `web/` app, so vinext is the default.

## Layout

| Path | Role |
|---|---|
| `app/` | Routes matching the live site (`/`, `/hu/`, `/services`, `/blog/<slug>`, service slugs at the root) |
| `lib/api.ts` | Django API client + bundled fallback JSON if the API is down |
| `lib/linkify.ts` | `[text](url)` + autolinks and FAQ `h3.faq-q` — same rules as PR #18 / Django `site_extras.linkify` + `faq_marked` / `js/main.js` (escaped; only `http(s)` and `/path`; external links `target=_blank rel=noopener`) |
| `public/css`, `public/js`, `public/assets` | Pixel-faithful CSS, interactivity, fonts, logos |
| `cloudflare.config.ts` | Worker name `infinitecare-next`, account `164584608fafa1395f843df7bb17e1c7` |

## API used (no Django schema change)

Public read-only JSON on `https://infinitecare-api.amyrsalarr.workers.dev`:

- `GET /api/settings/?lang=en|hu`
- `GET /api/home/?lang=`
- `GET /api/services/?lang=` (includes `slug`, `slugs.en/hu`, `blocks`, `meta_*`)
- `GET /api/gallery/?lang=` (photos, clips, YouTube)
- `GET /api/blog/?lang=` and `GET /api/blog/<slug>/?lang=` (`title`, `excerpt`, `body` as `blocks`, EN/HU via `?lang=`)

Contact form posts to `POST /api/contact/` on that origin, with same-origin `POST /api/contact` on this Worker as fallback.

No public endpoint is missing for blog/home/services. Bodies are already split into heading / paragraph / list blocks; this app applies `linkify` and FAQ marking at render time (the API does not need to change).

## Local development

Node.js 22+. From this directory:

```bash
npm install
npm run check          # linkify / FAQ markup parity with Django tests
npm run dev            # vinext + workerd (Vite). Open the printed localhost URL
```

Optional: `API_ORIGIN` if you point at another Django API. Defaults to the live API Worker.

## Build & local Worker preview

```bash
npm run build          # vite build → Cloudflare Worker output
npm run start          # vite preview (workerd) of the production build
```

Then check routes, for example:

```bash
curl -sI http://127.0.0.1:8787/services.html     # 301 → /services
curl -s http://127.0.0.1:8787/sitemap.xml
curl -s http://127.0.0.1:8787/blog/autumn-winter-skincare-routine | head
```

The preview port may differ; use the URL `npm run start` prints.

## Preview deploy (does not touch production DNS or `infinitecare-site`)

Account: `164584608fafa1395f843df7bb17e1c7`. Authenticate with `CLOUDFLARE_API_TOKEN` (or `npx cf auth login`).

```bash
export CLOUDFLARE_API_TOKEN=…
export CLOUDFLARE_ACCOUNT_ID=164584608fafa1395f843df7bb17e1c7
npm run deploy         # deploys Worker infinitecare-next
```

Expected preview host: `https://infinitecare-next.<subdomain>.workers.dev` (for this account, `infinitecare-next.amyrsalarr.workers.dev`).

KV namespace `VINEXT_KV_CACHE` is provisioned on first deploy for fetch/ISR cache. Page HTML uses Workers Cache with `export const revalidate = 180` (3 minutes).

## Caching

- `export const revalidate = 180` on pages, sitemap and `llms.txt`
- `fetch(..., { next: { revalidate: 180 } })` for API calls
- If the API errors or times out (~8s), bundled snapshots in `lib/fallback/` are used so the site still renders

Admin edits therefore appear within a few minutes (or on the next request after the cache goes stale). For faster updates later, you can add an on-demand revalidate route that the Django admin calls; it is not required for this port.

## Cutover (do this only when ready; not done by this PR)

The live site today is the **static** Worker `infinitecare-site` plus (on some hosts) Rackhost Apache serving the same repo root.

1. Deploy and soak-test `infinitecare-next` on `*.workers.dev`.
2. In the Cloudflare dashboard, add a **custom domain** `www.infinitecare.hu` to Worker **`infinitecare-next`** (not `infinitecare-site`). Cloudflare will attach the hostname to this Worker; do not change DNS records if `www` is already a Cloudflare-proxied record — swapping the Worker on the hostname is enough.
3. Confirm `infinitecare.hu` (apex) still redirects or CNAMEs to `www` as today.
4. Leave `infinitecare-site` deployed but unused so you can roll back by pointing the hostname back to it.
5. **Rackhost:** if `www` still has an A/CNAME to Rackhost (or if some traffic bypasses Cloudflare), either:
   - stop advertising that origin (DNS already on Cloudflare), or
   - on Rackhost, replace the document root with a short bounce (redirect everything to `https://www.infinitecare.hu`) / disable the vhost once Cloudflare is origin.
6. Keep `scripts/sync_from_api.sh` and `python manage.py export_static` working on `master` until you are confident; they are the rollback path for the static site.
7. After cutover, crawlers should see the same URLs (clean, no `.html`). `*.html` 301s are implemented in `middleware.ts`.

## URL map (preserved)

- EN: `/`, `/services`, `/blog`, `/blog/<slug>`
- HU: `/hu/`, `/hu/services`, `/hu/blog`, `/hu/blog/<slug>`
- Service landings (both languages, site root): `/carbon-peeling`, `/ems-treatment`, `/cellulite-therapy`, `/exosome-therapy`, `/brazilift-en`, `/laser-hair-removal`, `/mesotherapy`, `/face-lifting-en`, `/teeth-whitening` and HU slugs `/carbon-hamlasztas`, `/ems-testkezeles`, `/cellulit-terapia`, `/exoszoma-terapia`, `/brazilift`, `/lezeres-tartos-szortelenites`, `/mezoterapia`, `/face-lifting`, `/fogfeherites`
- Legacy 301s: `/home`, `/fooldal`, `/prices`, `/szolgaltatasaink`, `/araink`, and every `*.html` → clean URL
- Canonical host: `https://www.infinitecare.hu`
