"""Render the site from the database into plain HTML files for GitHub Pages (fallback without backend).

    python manage.py export_static            # writes ../index.html, ../services.html, ../prices.html, ../hu/*.html
    python manage.py export_static --api-url https://your-backend.example.com/api/contact/

Uploaded images are copied to ../assets/media/ so the exported pages work with relative paths.
"""
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from content import data
from content.views import page_context


class Command(BaseCommand):
    help = 'Export the DB-driven site as static HTML (EN in the repo root, HU in /hu/)'

    def add_arguments(self, parser):
        parser.add_argument('--out', default=str(settings.SITE_ROOT))
        parser.add_argument('--api-url', default=settings.STATIC_EXPORT_API_URL,
                            help="Contact API URL baked into the pages ('' = mailto fallback)")

    def handle(self, *args, out, api_url, **kw):
        out = Path(out)
        media_out = out / 'assets' / 'media'
        if Path(settings.MEDIA_ROOT).exists():
            shutil.rmtree(media_out, ignore_errors=True)
            shutil.copytree(settings.MEDIA_ROOT, media_out)
        n = 0
        for lang in settings.SITE_LANGUAGES:
            folder = out if lang == 'en' else out / lang
            folder.mkdir(parents=True, exist_ok=True)
            for page in data.PAGES:
                html = render_to_string(f'site/{page}.html', page_context(lang, page, data.ExportUrls(lang), api_url))
                (folder / f'{page}.html').write_text(html, encoding='utf-8')
                n += 1
        self.stdout.write(self.style.SUCCESS(f'Exported {n} pages to {out} (API: {api_url or "mailto fallback"})'))
