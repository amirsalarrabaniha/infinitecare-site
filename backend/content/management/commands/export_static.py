"""Render the site from the database into plain HTML files for GitHub Pages (fallback without backend).

    python manage.py export_static            # writes ../index.html, ../services.html, ../hu/*.html, ../blog/<slug>.html, ../hu/blog/<slug>.html
    python manage.py export_static --api-url https://your-backend.example.com/api/contact/

Uploaded images are copied to ../assets/media/ so the exported pages work with relative paths.
"""
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from content import data
from content.api_source import ApiSource
from content.views import alt_url, page_context


class Command(BaseCommand):
    help = 'Export the DB-driven site as static HTML (EN in the repo root, HU in /hu/)'

    def add_arguments(self, parser):
        parser.add_argument('--out', default=str(settings.SITE_ROOT))
        parser.add_argument('--site-url', default=settings.STATIC_EXPORT_SITE_URL,
                            help='Public origin (with trailing slash) used for canonical / hreflang / sitemap, e.g. https://example.com/')
        parser.add_argument('--clean-urls', action='store_true', default=settings.STATIC_EXPORT_CLEAN_URLS,
                            help='Use /services instead of /services.html in canonical / hreflang / sitemap (Cloudflare Workers assets)')
        parser.add_argument('--from-api', default='',
                            help='Base URL of the Django backend (e.g. https://infinitecare-api.amyrsalarr.workers.dev): '
                                 'read all content from its JSON API instead of the local database; media files are downloaded to assets/media/')
        parser.add_argument('--api-url', default=settings.STATIC_EXPORT_API_URL,
                            help="Contact API URL baked into the pages ('' = mailto fallback)")

    def handle(self, *args, out, api_url, site_url, clean_urls, from_api='', **kw):
        out = Path(out)
        settings.STATIC_EXPORT_SITE_URL = site_url if site_url.endswith('/') else site_url + '/'
        settings.STATIC_EXPORT_CLEAN_URLS = clean_urls
        for old in (out / 'blog', out / 'hu' / 'blog'):  # drop posts that were unpublished / deleted
            shutil.rmtree(old, ignore_errors=True)
        media_out = out / 'assets' / 'media'
        src = ApiSource(from_api, media_dir=media_out) if from_api else data
        if not from_api and Path(settings.MEDIA_ROOT).exists():
            shutil.copytree(settings.MEDIA_ROOT, media_out, dirs_exist_ok=True)   # keeps older files that live pages may still use
        n = 0
        for lang in settings.SITE_LANGUAGES:
            folder = out if lang == 'en' else out / lang
            folder.mkdir(parents=True, exist_ok=True)
            for page in data.PAGES:
                html = render_to_string(f'site/{page}.html', page_context(lang, page, data.ExportUrls(lang), api_url, src=src))
                (folder / f'{page}.html').write_text(html, encoding='utf-8')
                n += 1
            (folder / 'blog').mkdir(exist_ok=True)
            for post in src.published_posts():
                ctx = page_context(lang, 'blog_post', data.ExportUrls(lang, 'blog'), api_url, post=post, src=src)
                (folder / 'blog' / f'{post.slug}.html').write_text(render_to_string('site/blog_post.html', ctx), encoding='utf-8')
                n += 1
        if from_api:
            self.stdout.write(f'Media: {src.downloaded} downloaded, {len(src.media_names) - src.downloaded} already present')
        self.write_discovery_files(out, src)
        self.stdout.write(self.style.SUCCESS(f'Exported {n} pages to {out} (API: {api_url or "mailto fallback"})'))

    def write_discovery_files(self, out, src=data):
        """robots.txt, sitemap.xml (with hreflang alternates) and llms.txt, for the public origin."""
        base = settings.STATIC_EXPORT_SITE_URL
        posts = list(src.published_posts())
        pages = [(p, None) for p in data.PAGES] + [('blog', p.slug) for p in posts]
        rows = []
        for page, slug in pages:
            alts = {l: alt_url(l, page, slug) for l in settings.SITE_LANGUAGES}
            links = ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>' for l, u in alts.items())
            links += f'<xhtml:link rel="alternate" hreflang="x-default" href="{alts["en"]}"/>'
            lastmod = next((p.published_at.isoformat() for p in posts if p.slug == slug), '')
            for l, u in alts.items():
                rows.append(f'<url><loc>{u}</loc>{f"<lastmod>{lastmod}</lastmod>" if lastmod else ""}{links}</url>')
        (out / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                                         'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(rows) + '\n</urlset>\n', encoding='utf-8')
        (out / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {base}sitemap.xml\n', encoding='utf-8')
        s = src.site_settings('en')
        en = lambda page, slug=None: alt_url('en', page, slug)
        hu = lambda page, slug=None: alt_url('hu', page, slug)
        lines = [f'# Infinite Care Beauty Clinic', '',
                 f'> Beauty and aesthetic clinic in Budapest ({s["address"]}). Treatments such as microneedling, laser hair removal, EMSCULPT and teeth whitening. The website is available in English and Hungarian.', '',
                 '## Pages', '',
                 f'- [Home]({en("index")}): clinic introduction, photo gallery, treatment videos and the contact form',
                 f'- [Our treatments]({en("services")}): all treatments',
                 f'- [Blog]({en("blog")}): articles about treatments and skin care']
        lines += [f'- [{p.tr("title", "en")}]({en("blog", p.slug)})' for p in posts]
        lines += ['', '## Magyar', '',
                  f'- [Főoldal]({hu("index")})', f'- [Szolgáltatásaink]({hu("services")})', f'- [Blog]({hu("blog")})',
                  '', '## Contact', '', f'- Phone: {s["phone"]}', f'- E-mail: {s["email"]}', f'- Address: {s["address"]}, {s["city"]}']
        lines += [f'- Opening hours: {h}' for h in s['hours']]
        (out / 'llms.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
