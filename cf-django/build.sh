#!/usr/bin/env bash
# Copies the shared Django apps from ../backend into src/ and collects static files for Workers assets.
set -euo pipefail
cd "$(dirname "$0")"
for d in content contact templates; do rm -rf "src/$d"; cp -r "../backend/$d" "src/$d"; done
cp ../backend/config/urls.py src/config_urls.py
find src -name "__pycache__" -prune -exec rm -rf {} +
rm -f src/content/tests.py src/contact/tests.py
rm -rf staticfiles
WORKERS_CI=1 python3 src/manage.py collectstatic --noinput -v0
# Workers bundles only Python modules: ship the seed JSON as a .py module
touch src/content/seed/__init__.py
python3 -c "import json,sys; d=json.load(open('src/content/seed/initial_content.json',encoding='utf-8')); open('src/content/seed/seed_data.py','w',encoding='utf-8').write('DATA = '+repr(d)+'\n')"
# Workers adaptations of the shared code:
# - date_hierarchy / date list_filter generate SQL the Durable Object SQLite bridge rejects
sed -i "/date_hierarchy/d; s/list_filter = \['is_read', 'language', 'created_at'\]/list_filter = ['is_read', 'language']/" src/contact/admin.py
# - Django's i18n_catalog.js template is a .js file and is not bundled: ship it as a Python string
python3 -c "import django,pathlib; t=(pathlib.Path(django.__file__).parent/'views/templates/i18n_catalog.js').read_text(); open('src/app/i18n_js.py','w').write('TEMPLATE = '+repr(t)+'\n')"
