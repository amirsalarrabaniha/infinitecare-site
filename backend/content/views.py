import hashlib
import json
from functools import lru_cache

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from . import data, live
from .ui import UI

LANGS = settings.SITE_LANGUAGES


def alt_url(lang, page, slug=None):
    """Absolute URL (static export layout) of a page in a language, for hreflang / canonical / og tags.
    With STATIC_EXPORT_CLEAN_URLS (Cloudflare Workers assets: /services instead of /services.html) the .html is dropped."""
    base = settings.STATIC_EXPORT_SITE_URL + ('hu/' if lang == 'hu' else '')
    name = f'blog/{slug}' if slug else page
    if settings.STATIC_EXPORT_CLEAN_URLS:
        return base + ('' if name == 'index' else name)
    return base + f'{name}.html'


@lru_cache(maxsize=1)
def asset_version():
    """Short content hash of css/js, appended as ?v=… so they can be cached for a year (`_headers`)."""
    h = hashlib.md5()
    for f in ('css/style.css', 'js/main.js'):
        p = settings.SITE_ROOT / f
        h.update(p.read_bytes() if p.exists() else b'')
    return h.hexdigest()[:8]


def page_context(lang, page, urls, api_url, post=None, src=data):
    """`page` is one of data.PAGES, or 'blog_post' (then `post` is the BlogPost to show).
    `src` provides the content: `data` (database) or an `api_source.ApiSource` (JSON API of the Django backend)."""
    other = 'hu' if lang == 'en' else 'en'
    ui = UI[lang]
    slug = post.slug if post else None
    nav_keys = ['index', 'services', 'blog']
    site = src.site_settings(lang)
    nav = [dict(key='index', label=ui['nav'][0], href=urls.page('index')),
           dict(key='services', label=ui['nav'][1], href=urls.page('services'))]
    if site['offers_url']:   # external Fresha offers page, opens in a new tab
        nav.append(dict(key='offers', label=ui['nav'][2], href=site['offers_url'], external=True))
    nav.append(dict(key='blog', label=ui['nav'][3], href=urls.page('blog')))
    socials = src.socials(site, lang)
    ctx = dict(lang=lang, other=other, page=page, nav_key='blog' if page == 'blog_post' else page, ui=ui,
               title=ui['titles'][page] if not post else post.tr('title', lang), nav=nav, S=urls.static, v=asset_version(),
               urls={k: urls.page(k) for k in nav_keys},
               switch={l: urls.page('blog' if post else page, l, slug) for l in LANGS},
               alternates={l: alt_url(l, 'blog' if post else page, slug) for l in LANGS},
               site=site, socials=socials, api_url=api_url, post_tpl=urls.page('blog', slug='__SLUG__'), post_slugs=','.join(x.slug for x in src.published_posts()), description=f"{ui['desc']} {site['address']}")
    ctx['canonical'] = ctx['alternates'][lang]
    if page == 'index':
        yt = src.youtube(lang, urls)
        gallery = src.gallery(lang, urls)
        gallery_videos = [v for v in yt if v['gallery']]
        org = {'@context': 'https://schema.org', '@type': 'HealthAndBeautyBusiness', 'name': 'Infinite Care Beauty Clinic',
               'url': settings.STATIC_EXPORT_SITE_URL, 'telephone': site['phone'], 'email': site['email'],
               'address': site['address'] + ', ' + site['city'], 'sameAs': [x['url'] for x in socials]}
        if site['booking_url']:
            org['potentialAction'] = {'@type': 'ReserveAction', 'name': ui['book_online'], 'target': {'@type': 'EntryPoint', 'urlTemplate': site['booking_url'], 'actionPlatform': ['http://schema.org/DesktopWebPlatform', 'http://schema.org/MobileWebPlatform']}}
        home, counters, clips = src.home(lang, urls), src.counters(lang), src.clips(lang, urls)
        ctx.update(ld_json=json.dumps(org, ensure_ascii=False).replace('<', '\\u003c'), home=home, counters=counters,
                   fp=live.index_fps(home, counters, gallery, yt, clips),
                   gallery=gallery, gallery_videos=gallery_videos, gallery_filters=src.gallery_filters(gallery + gallery_videos, ui), clips=clips,
                   watch_featured=next((v for v in yt if v['featured']), None), watch_shorts=[v for v in yt if v['home'] and not v['featured']][:4])
    elif page == 'services':
        svcs = src.services(lang, urls)
        ctx.update(services=svcs, fp=dict(services=live.fp(svcs)),
                   hero_image=urls.static + 'assets/images/services.webp')
    elif page == 'blog':
        posts = src.blog_posts(lang, urls)
        ctx.update(posts=posts, fp=dict(blog=live.fp(live.no_url(posts))), hero_image=urls.static + 'assets/images/gallery/clinic-lounge.webp',
                   description=ui['blog_desc'])
    elif page == 'blog_post':
        p = src.blog_post(post, lang, urls)
        og = settings.STATIC_EXPORT_SITE_URL + 'assets/media/' + post.cover.name
        ld = dict({'@context': 'https://schema.org', '@type': 'BlogPosting'}, headline=p['title'], description=p['excerpt'],
                  datePublished=p['iso_date'], image=og, inLanguage=lang,
                  publisher={'@type': 'Organization', 'name': 'Infinite Care Beauty Clinic', 'sameAs': [x['url'] for x in socials]})
        more = [x for x in src.blog_posts(lang, urls) if x['slug'] != post.slug][:2]
        ctx.update(post=p, more_posts=more, fp=dict(post=live.fp(live.no_url([p])[0]), more=live.fp(live.no_url(more))), hero_image=p['cover'], canonical=ctx['alternates'][lang],
                   ld_json=json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c'), og_image_url=og, description=p['excerpt'])
    return ctx


def shell_context(lang, api_url, src, post):
    """Context of `blog/post.html`: an empty, noindex article page that main.js fills from the API for `?p=<slug>`.
    Posts published after the last export have no static page of their own; the live blog list links them here."""
    urls = data.ExportUrls(lang, 'blog')
    ctx = page_context(lang, 'blog_post', urls, api_url, post=post, src=src)
    blog = {l: alt_url(l, 'blog') for l in settings.SITE_LANGUAGES}
    ctx.update(shell=True, noindex=True, title='…', more_posts=[], fp=dict(post='', more=''), ld_json='{}', canonical=blog[lang],
               description=ctx['ui']['blog_desc'], hero_image=urls.static + 'assets/images/gallery/clinic-lounge.webp',
               post=dict(ctx['post'], slug='', title='…', excerpt='', date='', iso_date='', blocks=[], videos=[]),
               switch={l: urls.page('blog', l) for l in settings.SITE_LANGUAGES}, alternates=blog)
    return ctx


def root(request):
    pref = request.COOKIES.get('ic-lang')
    return redirect(f'/{pref if pref in LANGS else "en"}/')


def blog_post(request, lang, slug):
    if lang not in LANGS:
        raise Http404
    post = get_object_or_404(data.published_posts(), slug=slug)
    ctx = page_context(lang, 'blog_post', data.LiveUrls(lang), '/api/contact/', post=post)
    return render(request, 'site/blog_post.html', ctx)


def page(request, lang, name='index'):
    if lang not in LANGS or name not in data.PAGES:
        raise Http404
    ctx = page_context(lang, name, data.LiveUrls(lang), '/api/contact/')
    return render(request, f'site/{name}.html', ctx)


def legacy(request, name):  # old static URLs like /services.html, /hu/services.html
    return redirect(f'/{request.path.startswith("/hu/") and "hu" or "en"}/{"" if name == "index" else name + "/"}', permanent=True)


def legacy_post(request, slug):  # old static URLs like /blog/<slug>.html, /hu/blog/<slug>.html
    return redirect(f'/{request.path.startswith("/hu/") and "hu" or "en"}/blog/{slug}/', permanent=True)


# ---- read-only JSON API ----
def _lang(request):
    lang = request.GET.get('lang', 'en')
    return lang if lang in LANGS else 'en'


def _json(payload):
    return JsonResponse(payload, json_dumps_params={'ensure_ascii': False})


@require_GET
def api_settings(request):
    return _json(data.site_settings(_lang(request)))


@require_GET
def api_home(request):
    lang = _lang(request)
    return _json({**data.home(lang, _AbsUrls(request, lang)), 'counters': data.counters(lang)})


@require_GET
def api_services(request):
    lang = _lang(request)
    return _json({'results': data.services(lang, _AbsUrls(request, lang))})


@require_GET
def api_gallery(request):
    lang = _lang(request)
    urls = _AbsUrls(request, lang)
    return _json({'photos': data.gallery(lang, urls), 'videos': data.clips(lang, urls), 'youtube': data.youtube(lang, urls)})


@require_GET
def api_blog(request):
    lang = _lang(request)
    return _json({'results': data.blog_posts(lang, _AbsUrls(request, lang))})


@require_GET
def api_blog_post(request, slug):
    lang = _lang(request)
    post = get_object_or_404(data.published_posts(), slug=slug)
    return _json(data.blog_post(post, lang, _AbsUrls(request, lang)))


@require_GET


class _AbsUrls(data.LiveUrls):
    def __init__(self, request, lang):
        super().__init__(lang)
        self.request = request

    def media(self, f):
        return self.request.build_absolute_uri(f.url) if f else ''
