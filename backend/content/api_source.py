"""Content source that reads the JSON API of the Django backend (Cloudflare Worker) instead of the local database.

Same function names / return shapes as `content.data`, so `views.page_context(..., src=ApiSource(url))` renders exactly
the pages the database would render. Used by `export_static --from-api URL` (see scripts/sync_from_api.sh).

Media: the API returns absolute URLs (`<api>/media/…`). They are rewritten to the static layout (`assets/media/…`)
and the files are downloaded by `download_media()` (only files that are not on disk yet; names never change).
"""
import json
import shutil
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from . import data


class ApiError(RuntimeError):
    pass


class ApiSource:
    def __init__(self, base_url, media_dir=None, timeout=30):
        self.media_dir = Path(media_dir) if media_dir else None
        self.base = base_url.rstrip('/')
        self.timeout = timeout
        self._cache = {}
        self.media_names = set()
        self.downloaded = 0

    # ---- HTTP ----
    def _open(self, url):
        req = urllib.request.Request(url, headers={'User-Agent': 'infinitecare-sync/1.0', 'Accept': '*/*'})
        try:
            return urllib.request.urlopen(req, timeout=self.timeout)
        except Exception as e:
            raise ApiError(f'GET {url} failed: {e}') from e

    def get(self, path, lang):
        key = (path, lang)
        if key not in self._cache:
            with self._open(f'{self.base}{path}?lang={lang}') as r:
                self._cache[key] = json.loads(r.read().decode('utf-8'))
        return self._cache[key]

    # ---- media URL rewriting ----
    def _fix(self, obj, urls):
        prefix = self.base + '/media/'
        if isinstance(obj, str):
            if obj.startswith(prefix):
                name = urllib.parse.unquote(obj[len(prefix):])
                self._want(name)
                return urls.media(SimpleNamespace(name=name))
            return obj
        if isinstance(obj, list):
            return [self._fix(x, urls) for x in obj]
        if isinstance(obj, dict):
            return {k: self._fix(v, urls) for k, v in obj.items()}
        return obj

    def _want(self, name):
        """Remember a media file and download it right away if it is missing in `media_dir` (the `imgsize` template
        filter reads width/height from the file while the page is rendered). Names never change: new image = new name."""
        if name in self.media_names:
            return
        self.media_names.add(name)
        if self.media_dir is None:
            return
        dest = self.media_dir / name
        if dest.exists() and dest.stat().st_size:
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        with self._open(f'{self.base}/media/{urllib.parse.quote(name)}') as r, open(dest, 'wb') as f:  # seeded files redirect to /static/…
            shutil.copyfileobj(r, f)
        self.downloaded += 1

    # ---- same API as content.data ----
    socials = staticmethod(data.socials)                  # pure helpers (no DB access)
    gallery_filters = staticmethod(data.gallery_filters)

    def site_settings(self, lang):
        return self.get('/api/settings/', lang)

    def home(self, lang, urls):
        h = dict(self.get('/api/home/', lang))
        h.pop('counters', None)
        return self._fix(h, urls)

    def counters(self, lang):
        return self.get('/api/home/', lang)['counters']

    def services(self, lang, urls):
        return self._fix(self.get('/api/services/', lang)['results'], urls)

    def gallery(self, lang, urls):
        return self._fix(self.get('/api/gallery/', lang)['photos'], urls)

    def youtube(self, lang, urls):
        return self._fix(self.get('/api/gallery/', lang)['youtube'], urls)

    def clips(self, lang, urls):
        return self._fix(self.get('/api/gallery/', lang)['videos'], urls)

    def blog_posts(self, lang, urls):
        out = []
        for p in self._fix(self.get('/api/blog/', lang)['results'], urls):
            out.append(dict(p, url=urls.page('blog', slug=p['slug'])))
        return out

    def blog_post(self, post, lang, urls):
        p = self._fix(self.get(f'/api/blog/{post.slug}/', lang), urls)
        return dict(p, url=urls.page('blog', slug=p['slug']))

    def published_posts(self):
        """Stubs with what the exporter / page_context need: slug, titles, cover name, publication date."""
        en = self.get('/api/blog/', 'en')['results']
        hu = {p['slug']: p for p in self.get('/api/blog/', 'hu')['results']}
        out = []
        for p in en:
            cover = p['cover'][len(self.base + '/media/'):] if p['cover'].startswith(self.base + '/media/') else ''
            if cover:
                self._want(urllib.parse.unquote(cover))
            titles = {'en': p['title'], 'hu': hu.get(p['slug'], p)['title']}
            out.append(SimpleNamespace(slug=p['slug'], cover=SimpleNamespace(name=urllib.parse.unquote(cover)),
                                       published_at=date.fromisoformat(p['iso_date'][:10]),
                                       tr=lambda field, lang, _t=titles: _t[lang]))
        return out
