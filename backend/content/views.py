import hashlib
import json
from functools import lru_cache

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from . import data
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


def page_context(lang, page, urls, api_url, post=None):
    """`page` is one of data.PAGES, or 'blog_post' (then `post` is the BlogPost to show)."""
    other = 'hu' if lang == 'en' else 'en'
    ui = UI[lang]
    slug = post.slug if post else None
    nav_keys = ['index', 'services', 'prices', 'blog']
    nav = [dict(key='index', label=ui['nav'][0], href=urls.page('index')),
           dict(key='services', label=ui['nav'][1], href=urls.page('services')),
           dict(key='prices', label=ui['nav'][2], href=urls.page('prices')),
           dict(key='offers', label=ui['nav'][3], href=urls.page('services') + '#packages'),
           dict(key='blog', label=ui['nav'][4], href=urls.page('blog'))]
    site = data.site_settings(lang)
    socials = data.socials(site, lang)
    ctx = dict(lang=lang, other=other, page=page, nav_key='blog' if page == 'blog_post' else page, ui=ui,
               title=ui['titles'][page] if not post else post.tr('title', lang), nav=nav, S=urls.static, v=asset_version(),
               urls={k: urls.page(k) for k in nav_keys},
               switch={l: urls.page('blog' if post else page, l, slug) for l in LANGS},
               alternates={l: alt_url(l, 'blog' if post else page, slug) for l in LANGS},
               site=site, socials=socials, api_url=api_url, description=f"{ui['desc']} {site['address']}")
    ctx['canonical'] = ctx['alternates'][lang]
    if page == 'index':
        gallery = data.gallery(lang, urls)
        org = {'@context': 'https://schema.org', '@type': 'HealthAndBeautyBusiness', 'name': 'Infinite Care Beauty Clinic',
               'url': settings.STATIC_EXPORT_SITE_URL, 'telephone': site['phone'], 'email': site['email'],
               'address': site['address'] + ', ' + site['city'], 'sameAs': [x['url'] for x in socials]}
        ctx.update(ld_json=json.dumps(org, ensure_ascii=False).replace('<', '\\u003c'), home=data.home(lang, urls), counters=data.counters(lang),
                   gallery=gallery, gallery_filters=data.gallery_filters(gallery, ui), clips=data.clips(lang, urls))
    elif page == 'services':
        svcs = data.services(lang, urls)
        ctx.update(services_before=svcs[:5], services_after=svcs[5:], packages=data.packages(lang, urls),
                   hero_image=urls.static + 'assets/images/services.webp')
    elif page == 'blog':
        ctx.update(posts=data.blog_posts(lang, urls), hero_image=urls.static + 'assets/images/gallery/clinic-lounge.webp',
                   description=ui['blog_desc'])
    elif page == 'blog_post':
        p = data.blog_post(post, lang, urls)
        og = settings.STATIC_EXPORT_SITE_URL + 'assets/media/' + post.cover.name
        ld = dict({'@context': 'https://schema.org', '@type': 'BlogPosting'}, headline=p['title'], description=p['excerpt'],
                  datePublished=p['iso_date'], image=og, inLanguage=lang,
                  publisher={'@type': 'Organization', 'name': 'Infinite Care Beauty Clinic', 'sameAs': [x['url'] for x in socials]})
        ctx.update(post=p, hero_image=p['cover'], canonical=ctx['alternates'][lang],
                   ld_json=json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c'), og_image_url=og, description=p['excerpt'], more_posts=[x for x in data.blog_posts(lang, urls) if x['slug'] != post.slug][:2])
    else:
        ctx.update(categories=data.prices(lang), hero_image=urls.static + 'assets/images/prices.webp')
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


def legacy(request, name):  # old static URLs like /services.html, /hu/prices.html
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
def api_packages(request):
    lang = _lang(request)
    return _json({'results': data.packages(lang, _AbsUrls(request, lang))})


@require_GET
def api_gallery(request):
    lang = _lang(request)
    urls = _AbsUrls(request, lang)
    return _json({'photos': data.gallery(lang, urls), 'videos': data.clips(lang, urls)})


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
def api_prices(request):
    return _json({'results': data.prices(_lang(request))})


class _AbsUrls(data.LiveUrls):
    def __init__(self, request, lang):
        super().__init__(lang)
        self.request = request

    def media(self, f):
        return self.request.build_absolute_uri(f.url) if f else ''
