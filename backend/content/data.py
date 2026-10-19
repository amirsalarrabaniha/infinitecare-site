"""Turns DB content into plain dicts for one language. Used by the HTML views, the JSON API and the static exporter."""
from django.conf import settings

from .models import SiteSettings, HomePage, Counter, Service, Package, PriceCategory

PAGES = ('index', 'services', 'prices')


class LiveUrls:
    """URLs when Django serves the site (/en/…, /hu/…)."""
    static = settings.STATIC_URL

    def __init__(self, lang):
        self.lang = lang

    def page(self, name, lang=None):
        lang = lang or self.lang
        return f'/{lang}/' if name == 'index' else f'/{lang}/{name}/'

    def media(self, f):
        return f.url if f else ''


class ExportUrls:
    """Relative URLs for the static (GitHub Pages) export: EN in the root, HU in /hu/."""
    def __init__(self, lang):
        self.lang = lang
        self.prefix = '../' if lang == 'hu' else ''
        self.static = self.prefix

    def page(self, name, lang=None):
        lang = lang or self.lang
        if lang == self.lang:
            return f'{name}.html'
        return f'hu/{name}.html' if lang == 'hu' else f'../{name}.html'

    def media(self, f):
        return f'{self.prefix}assets/media/{f.name}' if f else ''


def paragraphs(text):
    return [p.strip() for p in text.replace('\r', '').split('\n\n') if p.strip()]


def lines(text):
    return [l.strip() for l in text.replace('\r', '').split('\n') if l.strip()]


def site_settings(lang):
    s = SiteSettings.load()
    return dict(phone=s.phone, phone_href=s.phone_href, email=s.email, address=s.tr('address', lang),
                hours=lines(s.tr('hours', lang)), tagline=s.tr('tagline', lang), city=s.city,
                facebook=s.facebook, instagram=s.instagram, youtube=s.youtube, map_embed=s.map_embed)


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
                contact_title=t('c_h'), contact_text=t('c_p'))


def counters(lang):
    return [dict(value=c.value, suffix=c.suffix, label=c.tr('label', lang)) for c in Counter.objects.filter(is_active=True)]


def services(lang, urls):
    return [dict(id=s.id, image=urls.media(s.image), eyebrow=s.tr('eyebrow', lang), title=s.tr('title', lang),
                 description=lines(s.tr('description', lang)), show_details=s.show_details, order=s.order)
            for s in Service.objects.filter(is_active=True)]


def packages(lang, urls):
    return [dict(id=p.id, name=p.tr('name', lang), items=lines(p.tr('items', lang)), price=p.price,
                 image=urls.media(p.image), order=p.order) for p in Package.objects.filter(is_active=True)]


def prices(lang):
    return [dict(id=c.id, title=c.tr('title', lang),
                 items=[dict(label=i.tr('label', lang), price=i.tr('price', lang), is_subheading=i.is_subheading)
                        for i in c.items.all()])
            for c in PriceCategory.objects.filter(is_active=True).prefetch_related('items')]
