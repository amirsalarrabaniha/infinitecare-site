import hashlib
import re
import json
from functools import lru_cache

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from . import data, live
from .ui import UI

LANGS = settings.SITE_LANGUAGES


# Home "Our treatments" slider: extra slides after the admin f1 image (file in assets/media/home/slider/, alt EN, alt HU).
HOME_SLIDES = [
    ('facial-device', 'Facial treatment with a professional device', 'Arckezelés professzionális géppel'),
    ('facial-care', 'Gentle facial care treatment', 'Kíméletes arcápoló kezelés'),
    ('treatment-room', 'Treatment room at Infinite Care', 'Kezelőszoba az Infinite Care-ben'),
    ('reception-hallway', 'Infinite Care clinic reception', 'Az Infinite Care klinika recepciója'),
    ('clinic-lounge', 'Infinite Care clinic lounge', 'Az Infinite Care klinika váróterme'),
]


def alt_url(lang, page, slug=None):
    """Absolute URL (static export layout) of a page in a language, for hreflang / canonical / og tags.
    With STATIC_EXPORT_CLEAN_URLS (Cloudflare Workers assets: /services instead of /services.html) the .html is dropped."""
    if page == 'service' and slug:   # service pages of both languages live in the site root: /carbon-peeling, /carbon-hamlasztas
        return settings.STATIC_EXPORT_SITE_URL + (slug if settings.STATIC_EXPORT_CLEAN_URLS else f'{slug}.html')
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


def to_ld(obj):
    return json.dumps(obj, ensure_ascii=False).replace('<', '\\u003c')


def absolute(u):
    """Relative asset URL of the export (../assets/media/x.webp) -> absolute URL on the public site, for og:image / JSON-LD."""
    if not u or u.startswith('http'):
        return u
    return settings.STATIC_EXPORT_SITE_URL + 'assets/' + u.split('assets/', 1)[1] if 'assets/' in u else ''


SEO = {   # <title> and meta description of the main pages (search snippets), per language
    'en': {'index': ('Infinite Care Beauty Clinic Budapest | Laser & Skin Treatments',
                     'Beauty clinic in Budapest VI: laser hair removal, teeth whitening, exosome therapy, mesotherapy, carbon peeling and body treatments. Book your visit.'),
           'services': ('Treatments in Budapest – Laser, Skin & Body | Infinite Care',
                        'All Infinite Care treatments in Budapest: laser hair removal, teeth whitening, exosome therapy, mesotherapy, carbon peeling, RF facelifting, EMS and cellulite therapy.'),
           'blog': ('Beauty & Skincare Blog | Infinite Care Budapest',
                    'Skincare tips and treatment guides from Infinite Care Beauty Clinic in Budapest: laser hair removal, skin quality, peels and more.'),
           'privacy': ('Privacy notice | Infinite Care Beauty Clinic',
                       'How Infinite Care Beauty Clinic in Budapest handles the personal data you send through the contact form and the discount sign-up.')},
    'hu': {'index': ('Infinite Care kozmetika Budapest | Lézeres szőrtelenítés',
                     'Kozmetika Budapest VI. kerületében: lézeres szőrtelenítés, fogfehérítés, exoszóma-terápia, mezoterápia, carbon hámlasztás és testkezelések. Foglalj online!'),
           'services': ('Kezelések Budapesten – lézer, arc és test | Infinite Care',
                        'Az Infinite Care kezelései Budapesten: lézeres szőrtelenítés, fogfehérítés, exoszóma-terápia, mezoterápia, carbon hámlasztás, RF arcfeszesítés, EMS és cellulitkezelés.'),
           'blog': ('Szépségápolási blog | Infinite Care Budapest',
                    'Bőrápolási tippek és kezelési útmutatók a budapesti Infinite Care Beauty Clinic-től: lézeres szőrtelenítés, bőrminőség, hámlasztás és még sok más.'),
           'privacy': ('Adatkezelési tájékoztató | Infinite Care Beauty Clinic',
                       'Hogyan kezeli a budapesti Infinite Care Beauty Clinic a kapcsolatfelvételi űrlapon és a kedvezmény-feliratkozáskor megadott személyes adatokat.')},
}
MAPS_URL = 'https://maps.google.com/?cid=7015004816567906002'   # the clinic's Google Maps place (from the map embed)
DAYS = {'mon': 'Monday', 'tue': 'Tuesday', 'wed': 'Wednesday', 'thu': 'Thursday', 'fri': 'Friday', 'sat': 'Saturday', 'sun': 'Sunday'}


def opening_hours(lines):
    """['Mon-Fri: 9 - 20', 'Sat: 9 - 15'] -> schema.org OpeningHoursSpecification list ([] if a line cannot be read)."""
    order = list(DAYS)
    out = []
    for line in lines or []:
        m = re.match(r'\s*([A-Za-z]{3})[a-z]*\.?\s*(?:[-–]\s*([A-Za-z]{3})[a-z]*\.?)?\s*:\s*(\d{1,2})(?::(\d\d))?\s*[-–]\s*(\d{1,2})(?::(\d\d))?', line)
        if not m or m[1].lower() not in DAYS or (m[2] and m[2].lower() not in DAYS):
            return []
        a, b = order.index(m[1].lower()), order.index((m[2] or m[1]).lower())
        out.append({'@type': 'OpeningHoursSpecification', 'dayOfWeek': [DAYS[d] for d in order[a:b + 1]],
                    'opens': f'{int(m[3]):02d}:{m[4] or "00"}', 'closes': f'{int(m[5]):02d}:{m[6] or "00"}'})
    return out


def og_image(rel):
    """1200x630 JPEG crop (assets/images/og/<name>.jpg) of a site image for og:image / twitter:image; the original if it cannot be made."""
    if not rel or 'assets/' not in rel:
        return absolute(rel)
    name = rel.split('assets/', 1)[1].split('?')[0]
    srcf = settings.SITE_ROOT / 'assets' / name
    stem = name.rsplit('.', 1)[0].replace('/', '-')
    dst = settings.SITE_ROOT / 'assets' / 'images' / 'og' / f'{stem}.jpg'
    if not dst.exists():
        try:
            from PIL import Image, ImageOps
            dst.parent.mkdir(parents=True, exist_ok=True)
            ImageOps.fit(Image.open(srcf).convert('RGB'), (1200, 630), Image.LANCZOS, centering=(0.5, 0.4)).save(dst, 'JPEG', quality=82, optimize=True, progressive=True)
        except Exception:
            return absolute(rel)
    return settings.STATIC_EXPORT_SITE_URL + f'assets/images/og/{stem}.jpg'


def business(site, socials, ui, lang):
    """The clinic as a schema.org local business (home page @graph; referenced by @id from the other pages)."""
    base = settings.STATIC_EXPORT_SITE_URL
    street = re.sub(r'^\s*Bp\.\s*VI\.\s*', '', site['address']).replace(' str.', ' utca')
    org = {'@type': ['BeautySalon', 'HealthAndBeautyBusiness'], '@id': base + '#clinic', 'name': 'Infinite Care Beauty Clinic',
           'url': base, 'logo': base + 'assets/images/infinitecare-logo-1.png', 'image': og_image('assets/images/gallery/clinic-lounge.webp'),
           'telephone': site['phone'], 'email': site['email'], 'slogan': site.get('tagline') or None,
           'address': {'@type': 'PostalAddress', 'streetAddress': street, 'addressLocality': 'Budapest', 'postalCode': '1065', 'addressRegion': 'VI. kerület', 'addressCountry': 'HU'},
           'hasMap': MAPS_URL, 'areaServed': {'@type': 'City', 'name': 'Budapest'}, 'sameAs': [x['url'] for x in socials],
           'knowsLanguage': ['en', 'hu']}
    hours = opening_hours(site.get('hours'))
    if hours:
        org['openingHoursSpecification'] = hours
    if site.get('booking_url'):
        org['potentialAction'] = {'@type': 'ReserveAction', 'name': ui['book_online'], 'target': {'@type': 'EntryPoint', 'urlTemplate': site['booking_url'], 'inLanguage': lang, 'actionPlatform': ['https://schema.org/DesktopWebPlatform', 'https://schema.org/MobileWebPlatform']}}
    return {k: v for k, v in org.items() if v}


def website(lang):
    base = settings.STATIC_EXPORT_SITE_URL
    return {'@type': 'WebSite', '@id': base + '#website', 'url': base, 'name': 'Infinite Care Beauty Clinic', 'inLanguage': ['en', 'hu'], 'publisher': {'@id': base + '#clinic'}}


def crumbs(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': n, 'item': u} for i, (n, u) in enumerate(items, 1)]}


def service_pair(src, service_id, urls):
    """The service in both languages ({'en': {...}, 'hu': {...}}), as `data.services` returns it."""
    return {l: next(x for x in src.services(l, urls) if x['id'] == service_id) for l in LANGS}


def page_context(lang, page, urls, api_url, post=None, src=data, service_id=None):
    """`page` is one of data.PAGES, 'blog_post' (then `post` is the BlogPost to show)
    or 'service' (the landing page of the service `service_id`, e.g. /carbon-peeling).
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
               title=ui['titles'].get(page, '') if not post else post.tr('title', lang), nav=nav, S=urls.static, v=asset_version(),
               urls={k: urls.page(k) for k in nav_keys},
               switch={l: urls.page('blog' if post else page, l, slug) for l in LANGS},
               alternates={l: alt_url(l, 'blog' if post else page, slug) for l in LANGS},
               site=site, socials=socials, api_url=api_url, post_tpl=urls.page('blog', slug='__SLUG__'), post_slugs=','.join(x.slug for x in src.published_posts()), description=f"{ui['desc']} {site['address']}",
               privacy_url=urls.page('privacy'))
    if page in SEO[lang]:
        ctx.update(page_title=SEO[lang][page][0], description=SEO[lang][page][1])
    if page == 'service':
        pair = service_pair(src, service_id, urls)
        svc = pair[lang]
        # a language without its own page of this service falls back to its services page
        ctx.update(switch={l: urls.service(x['slug']) if x['slug'] else urls.page('services', l) for l, x in pair.items()},
                   alternates={l: alt_url(l, 'service', x['slug']) if x['slug'] else alt_url(l, 'services') for l, x in pair.items()})
    ctx['canonical'] = ctx['alternates'][lang]
    if page == 'service':
        cat = svc['gallery_category']
        photos = [g for g in src.gallery(lang, urls) if g['category'] == cat][:9] if cat else []
        others = [dict(title=x['title'], href=urls.service(x['slug'])) for x in src.services(lang, urls) if x['slug'] and x['id'] != svc['id']]
        home = alt_url(lang, 'index')
        image = absolute(svc['image'])
        graph = [{'@type': 'Service', '@id': ctx['canonical'] + '#service', 'name': svc['title'], 'serviceType': svc['title'],
                  'description': svc['meta_description'] or ' '.join(svc['description']), 'url': ctx['canonical'], 'inLanguage': lang,
                  **({'image': image} if image else {}), 'areaServed': {'@type': 'City', 'name': 'Budapest'},
                  'provider': business(site, socials, ui, lang)},
                 crumbs([(ui['nav'][0], home), (ui['nav'][1], alt_url(lang, 'services')), (svc['title'], ctx['canonical'])])]
        ctx.update(svc=svc, photos=photos, others=others, title=svc['title'], nav_key='services',
                   page_title=f"{svc['meta_title']} | Infinite Care", description=svc['meta_description'] or ctx['description'],
                   hero_image=svc['image'], og_image_url=og_image(svc['image']) or image, fp=dict(svc=live.svc_fp(svc)),
                   ld_json=to_ld({'@context': 'https://schema.org', '@graph': graph}))
    elif page == 'index':
        yt = src.youtube(lang, urls)
        gallery = src.gallery(lang, urls)
        gallery_videos = [v for v in yt if v['gallery']]
        org = {'@context': 'https://schema.org', '@graph': [business(site, socials, ui, lang), website(lang)]}
        home, counters, clips = src.home(lang, urls), src.counters(lang), src.clips(lang, urls)
        ctx.update(ld_json=json.dumps(org, ensure_ascii=False).replace('<', '\\u003c'), home=home, counters=counters,
                   fp=live.index_fps(home, counters, gallery, yt, clips),
                   gallery=gallery, gallery_videos=gallery_videos, gallery_filters=src.gallery_filters(gallery + gallery_videos, ui), clips=clips,
                   watch_featured=next((v for v in yt if v['featured']), None), watch_shorts=[v for v in yt if v['home'] and not v['featured']][:4],
                   slider_slides=HOME_SLIDES, og_image_url=og_image(home['hero_image']))
    elif page == 'services':
        svcs = src.services(lang, urls)
        f = live.fp(svcs)
        for x in svcs:   # link of the card to the service's own page (not part of the fingerprint, the API has no site URLs)
            x['href'] = urls.service(x['slug']) if x.get('slug') else ''
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', '@id': ctx['canonical'] + '#page', 'url': ctx['canonical'], 'name': ctx['page_title'], 'inLanguage': lang, 'isPartOf': {'@id': settings.STATIC_EXPORT_SITE_URL + '#website'},
             'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': x['title'], **({'url': alt_url(lang, 'service', x['slug'])} if x.get('slug') else {})} for i, x in enumerate(svcs, 1)]}},
            crumbs([(ui['nav'][0], alt_url(lang, 'index')), (ui['nav'][1], ctx['canonical'])])]}
        ctx.update(services=svcs, fp=dict(services=f), ld_json=to_ld(ld), og_image_url=og_image('assets/images/services.webp'),
                   hero_image=urls.static + 'assets/images/services.webp')
    elif page == 'blog':
        posts = src.blog_posts(lang, urls)
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'Blog', '@id': ctx['canonical'] + '#blog', 'url': ctx['canonical'], 'name': ctx['page_title'], 'inLanguage': lang, 'publisher': {'@id': settings.STATIC_EXPORT_SITE_URL + '#clinic'},
             'blogPost': [{'@type': 'BlogPosting', 'headline': x['title'], 'url': alt_url(lang, 'blog', x['slug']), 'datePublished': x['iso_date']} for x in posts]},
            crumbs([(ui['nav'][0], alt_url(lang, 'index')), (ui['nav'][3], ctx['canonical'])])]}
        ctx.update(posts=posts, fp=dict(blog=live.fp(live.no_url(posts))), hero_image=urls.static + 'assets/images/gallery/clinic-lounge.webp',
                   ld_json=to_ld(ld), og_image_url=og_image('assets/images/gallery/clinic-lounge.webp'))
    elif page == 'privacy':
        ctx.update(hero_image=urls.static + 'assets/images/gallery/clinic-lounge.webp', og_image_url=og_image('assets/images/gallery/clinic-lounge.webp'))
    elif page == 'blog_post':
        p = src.blog_post(post, lang, urls)
        og = og_image('assets/media/' + post.cover.name)
        cover = settings.STATIC_EXPORT_SITE_URL + 'assets/media/' + post.cover.name
        clinic = {'@type': 'Organization', '@id': settings.STATIC_EXPORT_SITE_URL + '#clinic', 'name': 'Infinite Care Beauty Clinic', 'url': settings.STATIC_EXPORT_SITE_URL,
                  'logo': {'@type': 'ImageObject', 'url': settings.STATIC_EXPORT_SITE_URL + 'assets/images/infinitecare-logo-1.png'}, 'sameAs': [x['url'] for x in socials]}
        ld = {'@context': 'https://schema.org', '@graph': [
            dict({'@type': 'BlogPosting', '@id': ctx['canonical'] + '#post'}, headline=p['title'][:110], description=p['excerpt'],
                 datePublished=p['iso_date'], dateModified=p.get('updated') or p['iso_date'], image=[cover, og] if og != cover else cover, inLanguage=lang,
                 mainEntityOfPage=ctx['canonical'], author=clinic, publisher=clinic),
            crumbs([(ui['nav'][0], alt_url(lang, 'index')), (ui['nav'][3], alt_url(lang, 'blog')), (p['title'], ctx['canonical'])])]}
        more = [x for x in src.blog_posts(lang, urls) if x['slug'] != post.slug][:2]
        ctx.update(post=p, more_posts=more, fp=dict(post=live.fp(live.no_url([p])[0]), more=live.fp(live.no_url(more))), hero_image=p['cover'], canonical=ctx['alternates'][lang],
                   ld_json=to_ld(ld), og_image_url=og, description=p['excerpt'],
                   page_title=f"{p['title']} | Infinite Care")
    return ctx


def shell_context(lang, api_url, src, post):
    """Context of `blog/post.html`: an empty, noindex article page that main.js fills from the API for `?p=<slug>`.
    Posts published after the last export have no static page of their own; the live blog list links them here."""
    urls = data.ExportUrls(lang, 'blog')
    ctx = page_context(lang, 'blog_post', urls, api_url, post=post, src=src)
    blog = {l: alt_url(l, 'blog') for l in settings.SITE_LANGUAGES}
    ctx.update(shell=True, noindex=True, title='…', page_title='', more_posts=[], fp=dict(post='', more=''), ld_json='{}', canonical=blog[lang],
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


def service_page(request, slug):
    """/carbon-peeling/ (EN) or /carbon-hamlasztas/ (HU): the landing page of one service."""
    for lang in LANGS:
        svc = data.Service.objects.filter(is_active=True, **{f'slug_{lang}': slug}).first()
        if svc:
            return render(request, 'site/service_page.html', page_context(lang, 'service', data.LiveUrls(lang), '/api/contact/', service_id=svc.id))
    raise Http404


def page(request, lang, name='index'):
    if lang not in LANGS:
        if name == 'index':
            return service_page(request, lang)
        raise Http404
    if name not in data.PAGES:
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
