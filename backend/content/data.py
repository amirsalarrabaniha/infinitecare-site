"""Turns DB content into plain dicts for one language. Used by the HTML views, the JSON API and the static exporter."""
import posixpath

from django.conf import settings
from django.utils.safestring import mark_safe

from .ui import UI
from .models import TREATMENT_TYPES, SiteSettings, HomePage, Counter, Service, GalleryItem, VideoClip, YouTubeVideo, BlogPost

PAGES = ('index', 'services', 'blog')   # pages with one HTML file per language; blog posts are exported separately


class LiveUrls:
    """URLs when Django serves the site (/en/…, /hu/…)."""
    static = settings.STATIC_URL

    def __init__(self, lang):
        self.lang = lang

    def page(self, name, lang=None, slug=None):
        lang = lang or self.lang
        if slug:
            return f'/{lang}/blog/{slug}/'
        return f'/{lang}/' if name == 'index' else f'/{lang}/{name}/'

    def media(self, f):
        return f.url if f else ''


class ExportUrls:
    """Relative URLs for the static export: EN in the root, HU in /hu/, blog posts in blog/ (EN) and hu/blog/ (HU).
    `subdir` is the folder of the page being rendered below its language root ('' or 'blog')."""
    def __init__(self, lang, subdir=''):
        self.lang = lang
        self.cur = ('hu/' if lang == 'hu' else '') + (subdir + '/' if subdir else '')
        self.prefix = '../' * self.cur.count('/')
        self.static = self.prefix

    def page(self, name, lang=None, slug=None):
        lang = lang or self.lang
        target = ('hu/' if lang == 'hu' else '') + (f'blog/{slug}.html' if slug else f'{name}.html')
        return posixpath.relpath(target, self.cur.rstrip('/') or '.')

    def media(self, f):
        return f'{self.prefix}assets/media/{f.name}' if f else ''


def paragraphs(text):
    return [p.strip() for p in text.replace('\r', '').split('\n\n') if p.strip()]


def lines(text):
    return [l.strip() for l in text.replace('\r', '').split('\n') if l.strip()]


SOCIAL_ICONS = {
    'facebook': '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path fill="currentColor" d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"/></svg>',
    'instagram': '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path fill="currentColor" d="M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077"/></svg>',
    'youtube': '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path fill="currentColor" d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>',
    'tiktok': '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>',
}
SOCIAL_NAMES = {'facebook': 'Facebook', 'instagram': 'Instagram', 'youtube': 'YouTube', 'tiktok': 'TikTok'}


def socials(site, lang):
    """Icon links for the footer / contact section, only for the networks that have a URL (editable in Site settings)."""
    out = []
    for key, name in SOCIAL_NAMES.items():
        url = site[key]
        if url:
            out.append(dict(key=key, name=name, url=url, icon=mark_safe(SOCIAL_ICONS[key]),
                            label=UI[lang]['soc'].format(name=name)))
    return out


def site_settings(lang):
    s = SiteSettings.load()
    return dict(phone=s.phone, phone_href=s.phone_href, email=s.email, address=s.tr('address', lang),
                hours=lines(s.tr('hours', lang)), tagline=s.tr('tagline', lang), city=s.city,
                facebook=s.facebook, instagram=s.instagram, youtube=s.youtube, tiktok=s.tiktok, booking_url=s.booking_url, offers_url=s.offers_url, map_embed=s.map_embed)


def home(lang, urls):
    h = HomePage.load()
    t = lambda f: h.tr(f, lang)
    h1 = t('h1').split('|', 1)
    sec = lambda n: dict(image=urls.media(getattr(h, f'{n}_image')), eyebrow=t(f'{n}_eyebrow'), title=t(f'{n}_title'),
                         paragraphs=paragraphs(t(f'{n}_text')), button=t(f'{n}_button'))
    return dict(hero_image=urls.media(h.hero_image), hello=t('hello'), h1_main=h1[0].strip(),
                h1_em=h1[1].strip() if len(h1) > 1 else '', lead=t('lead'),
                marquee=[m.strip() for m in t('marquee').split(',') if m.strip()],
                f1=sec('f1'), f2=sec('f2'), cta_image=urls.media(h.cta_image), cta_script=t('cta_s'),
                cta_title=t('cta'), cta_button=t('cta_b'), contact_eyebrow=t('contact'),
                contact_title=t('c_h'), contact_text=t('c_p'), contact_image=urls.media(h.contact_image))


def counters(lang):
    return [dict(value=c.value, suffix=c.suffix, label=c.tr('label', lang)) for c in Counter.objects.filter(is_active=True)]


def services(lang, urls):
    vids = [v for v in youtube(lang, urls) if v['service_id']]
    return [dict(videos=[v for v in vids if v['service_id'] == s.id][:2], id=s.id, image=urls.media(s.image), eyebrow=s.tr('eyebrow', lang), title=s.tr('title', lang),
                 description=lines(s.tr('description', lang)), order=s.order)
            for s in Service.objects.filter(is_active=True)]


def gallery(lang, urls):
    return [dict(id=g.id, image=urls.media(g.image), category=g.category,
                 cats=_cats(g.category), alt=g.tr('alt', lang),
                 width=g.width, height=g.height) for g in GalleryItem.objects.filter(is_active=True)]


def _cats(category):
    return ' '.join([category] + (['treatments'] if category in TREATMENT_TYPES else []))


def youtube(lang, urls):
    """YouTube videos for one site language: those for both languages plus the ones made for `lang`."""
    return [dict(id=v.id, youtube_id=v.youtube_id, title=v.tr('title', lang), caption=v.tr('caption', lang), poster=urls.media(v.poster),
                 width=v.poster_width, height=v.poster_height, vertical=v.vertical, category=v.category, cats=_cats(v.category),
                 featured=v.featured, home=v.show_on_home, gallery=v.show_in_gallery, service_id=v.service_id, post_id=v.post_id)
            for v in YouTubeVideo.objects.filter(is_active=True, language__in=['', lang])]


def clips(lang, urls):
    return [dict(id=c.id, video=urls.media(c.video), poster=urls.media(c.poster), title=c.tr('title', lang), category=c.category)
            for c in VideoClip.objects.filter(is_active=True)]


MONTHS = {
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    'hu': ['január', 'február', 'március', 'április', 'május', 'június', 'július', 'augusztus', 'szeptember', 'október', 'november', 'december'],
}


def nice_date(d, lang):
    m = MONTHS[lang][d.month - 1]
    return f'{d.year}. {m} {d.day}.' if lang == 'hu' else f'{m} {d.day}, {d.year}'


def body_blocks(text):
    """Very small markup: '## ' heading, '- ' list, everything else paragraphs (rendered escaped by the template)."""
    blocks = []
    for chunk in paragraphs(text):
        ls = [l.strip() for l in chunk.split('\n') if l.strip()]
        if chunk.startswith('## '):
            blocks.append(dict(type='h', text=chunk[3:].strip()))
        elif all(l.startswith('- ') for l in ls):
            blocks.append(dict(type='ul', items=[l[2:].strip() for l in ls]))
        else:
            blocks.append(dict(type='p', text=' '.join(ls)))
    return blocks


def published_posts():
    return BlogPost.objects.filter(is_published=True)


def post_summary(p, lang, urls):
    return dict(slug=p.slug, title=p.tr('title', lang), excerpt=p.tr('excerpt', lang), cover=urls.media(p.cover),
                date=nice_date(p.published_at, lang), iso_date=p.published_at.isoformat(), url=urls.page('blog', slug=p.slug))


def blog_posts(lang, urls):
    return [post_summary(p, lang, urls) for p in published_posts()]


def blog_post(post, lang, urls):
    return dict(post_summary(post, lang, urls), blocks=body_blocks(post.tr('body', lang)),
                videos=[v for v in youtube(lang, urls) if v['post_id'] == post.id])


def gallery_filters(items, ui):
    """Filter tabs for the gallery: "All" plus every category that has at least one photo or video (never an empty tab)."""
    used = {c for g in items for c in g['cats'].split()}
    return [(k, label) for k, label in ui['gal_filters'] if k == 'all' or k in used]
