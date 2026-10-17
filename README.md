# Wingu Elite Adventures

Luxury Kenya safari website. Built by [polycarp dev](https://linktr.ee/polycarpdev).

```
backend/   Django: admin (content), cockpit (bookings & messages), form API, content export
web/       Astro: the public site, built to static HTML
deploy/    deploy.sh, rebuild.sh (cron), Apache .htaccess template
brand/     logo sources
```

## How it works

1. Staff edit content in **/admin/**. Saving any content model sets `backend/var/rebuild.flag`.
2. `deploy/rebuild.sh` (cron, every 5 min) sees the flag, runs `manage.py export_content`
   (writes `web/src/data/content.json` and WebP image renditions via Pillow), builds the
   Astro site and syncs it to the document root. No flag → it exits instantly.
3. Apache serves the static pages. Only `/admin`, `/cockpit`, `/api` and `/ckeditor5`
   reach Django (Passenger). Booking/contact forms POST JSON to `/api/…`.

Navigation is instant after the first load (`<ClientRouter />` + viewport prefetch).
Sizes are in `rem` with a viewport-proportional root size from 1100px up, so laptops at
100/125/150% zoom see the same layout.

## Cockpit (staff area)

`/cockpit/` on the live domain (locally: `localhost:4321/cockpit/` with both dev servers running).
Staff accounts need **Staff status**; create the first with `manage.py createsuperuser`.

- **Dashboard:** visitors, bookings, pipeline value, upcoming trips, latest enquiries
- **Analytics:** cookie-less page views from the public site (`/api/hit/`), no consent banner needed
- **Reports:** bookings per month, status funnel, destinations, packages, lead sources, CSV export
- **Bookings / Messages:** search, status workflow, internal notes, one-click email/WhatsApp/call
- **Website content:** safaris (with day-by-day itinerary), destinations, blog, gallery
  (multi-photo upload), testimonials, team, FAQs. Saving publishes within ~5 minutes.

Same stylesheet as the public site (`web/src/styles/global.css` served as `/static/site/global.css`)
plus `backend/static/cockpit/`. Navigation is instant (prefetch + DOM swap in `cockpit.js`).
`/admin/` remains for superusers (users & permissions).

## Local development

```bash
python3 -m venv venv && venv/bin/pip install -r backend/requirements.txt
cp backend/.env.example backend/.env       # set DEBUG=True, ALLOWED_HOSTS=localhost,127.0.0.1
venv/bin/python backend/manage.py migrate
venv/bin/python backend/manage.py export_content
venv/bin/python backend/manage.py runserver            # :8000

cd web && npm ci && npm run dev                         # :4321 (proxies /api and /media to :8000)
# Django on another port?  API_ORIGIN=http://127.0.0.1:8001 npm run dev
```

Tests: `venv/bin/python backend/manage.py test api cockpit`

## Dependency rules (shared hosting)

- Python: prebuilt wheels only (`pip install --only-binary=:all:`).
- Node: `astro` is the only dependency. Rollup runs as WebAssembly (`@rollup/wasm-node`),
  `sharp` and the Rust LZMA module are stubbed (`web/stubs/empty`). Images are handled by
  Pillow in Django. The only native binary is esbuild, pinned to one thread.
- Builds run under `nice`/`ionice`, `GOMAXPROCS=1`, `UV_THREADPOOL_SIZE=1`, with a lock.

## Server setup (once)

1. cPanel → **PostgreSQL Databases**: create a database and user.
2. `git clone https://github.com/polycarpdev/WinguEliteAdventures.git ~/winguelite`
3. cPanel → **Setup Python App**: Python 3.13, app root `winguelite/backend`,
   startup file `passenger_wsgi.py`, entry point `application`.
4. cPanel → **Setup Node.js App**: Node ≥ 22.12, app root `winguelite/web`
   (only used for its `node`/`npm` binaries; the app itself need not run).
5. `cp backend/.env.example backend/.env` and fill in (`DATABASE_URL`, SMTP, `SECRET_KEY`).
6. `cp deploy/config.example.sh deploy/config.sh` and set the paths cPanel showed you.
7. `deploy/deploy.sh`, then `backend/manage.py createsuperuser`.
8. cPanel → **Cron Jobs**:
   `*/5 * * * * $HOME/winguelite/deploy/rebuild.sh >> $HOME/winguelite/backend/var/rebuild.log 2>&1`

## Deploying changes

```bash
git push                        # locally
ssh … '~/winguelite/deploy/deploy.sh'   # on the server: pull, migrate, build, publish, restart
```
