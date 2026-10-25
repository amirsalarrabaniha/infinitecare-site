"""Turns DB content into plain dicts for one language. Used by the HTML views, the JSON API and the static exporter."""
import posixpath

from django.conf import settings

from .models import SiteSettings, HomePage, Counter, Service, Package, PriceCategory, GalleryItem, VideoClip, BlogPost

PAGES = ('index', 'services', 'prices', 'blog')   # pages with one HTML file per language; blog posts are exported separately


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
                contact_title=t('c_h'), contact_text=t('c_p'), contact_image=urls.media(h.contact_image))


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


def gallery(lang, urls):
    return [dict(id=g.id, image=urls.media(g.image), category=g.category, alt=g.tr('alt', lang),
                 width=g.width, height=g.height) for g in GalleryItem.objects.filter(is_active=True)]


def clips(lang, urls):
    return [dict(id=c.id, video=urls.media(c.video), poster=urls.media(c.poster), title=c.tr('title', lang))
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
    return dict(post_summary(post, lang, urls), blocks=body_blocks(post.tr('body', lang)))
