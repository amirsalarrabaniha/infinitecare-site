#!/usr/bin/env bash
# Regenerate the static site from the content managed in the admin (https://infinitecare-api.amyrsalarr.workers.dev/admin/).
#
#   scripts/sync_from_api.sh            pull content from the API, rewrite the static pages + assets/media in this repo
#   scripts/sync_from_api.sh --check    same, but only report whether the repo is out of date (exit 1 if so; nothing is kept)
#
# Reads the public JSON API (/api/settings/, /api/home/, /api/services/, /api/gallery/, /api/blog/) – no secrets needed.
# Afterwards: review `git diff`, commit, and deploy (see README "Publish changes made in the admin").
#
# Env: API_URL (default below), SITE_URL (public origin used for canonical/hreflang/sitemap),
#      SYNC_PYTHON (a python with Django + Pillow; default: .sync-venv created on first run).
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
API_URL="${API_URL:-https://infinitecare-api.amyrsalarr.workers.dev}"
SITE_URL="${SITE_URL:-https://www.infinitecare.hu/}"

PY="${SYNC_PYTHON:-}"
if [ -z "$PY" ]; then
  if [ ! -x .sync-venv/bin/python ]; then
    python3 -m venv .sync-venv
    .sync-venv/bin/pip install -q "Django>=5.2,<7" "Pillow>=10"   # Pillow: width/height attributes (CLS) come from the image files
  fi
  PY="$ROOT/.sync-venv/bin/python"
fi

run_export() {   # $1 = repo root to write into
  (cd "$1/backend" && SECRET_KEY=sync DEBUG=True MEDIA_ROOT="$1/assets/media" "$PY" manage.py export_static \
    --out "$1" --from-api "$API_URL" --site-url "$SITE_URL" --clean-urls --api-url "$API_URL/api/contact/")
  python3 "$ROOT/scripts/html_redirects.py" "$1"
}

if [ "${1:-}" = "--check" ]; then
  # export into a copy of the committed state and compare, so local work is never touched
  TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
  mkdir "$TMP/base" "$TMP/new"
  git archive HEAD | tar -x -C "$TMP/base"; git archive HEAD | tar -x -C "$TMP/new"
  run_export "$TMP/new" >/dev/null
  if diff -rq -x backend -x cf-django -x '__pycache__' "$TMP/base" "$TMP/new"; then
    echo "Site is up to date with the admin."
  else
    echo "Site is OUT OF DATE vs the admin: run scripts/sync_from_api.sh, commit, deploy."; exit 1
  fi
else
  run_export "$ROOT"
  echo "Done. Review: git status && git diff --stat   (then commit + deploy, see README)"
fi
