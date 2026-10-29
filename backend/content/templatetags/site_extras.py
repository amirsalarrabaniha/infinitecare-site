"""Template helpers: intrinsic image size (prevents layout shift) and short type-safe helpers."""
from functools import lru_cache
from pathlib import Path

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


def _resolve(url):
    """Map a rendered URL ('../assets/media/home/x.webp', '/media/x.webp', '/static/assets/images/x.png') to a file."""
    url = str(url or '').split('?')[0]
    for marker, root in (('assets/media/', Path(settings.MEDIA_ROOT)), ('/media/', Path(settings.MEDIA_ROOT)),
                         ('assets/images/', settings.SITE_ROOT / 'assets' / 'images')):
        if marker in url:
            return root / url.split(marker, 1)[1]
    return None


@lru_cache(maxsize=512)
def _size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:  # Pillow or the file is not available (e.g. on the Workers runtime): no size attributes
        return None


@register.filter
def imgsize(url):
    """`{{ url|imgsize }}` -> `width="1206" height="783"` (or nothing if the file cannot be read)."""
    p = _resolve(url)
    s = _size(str(p)) if p else None
    return mark_safe(f'width="{s[0]}" height="{s[1]}"') if s else ''


_LINK_RE = None


FAQ_RE = r'^\s*(frequently asked questions|gyakran ism[eé]telt k[eé]rd[eé]sek|faq)\b'


@register.filter
def faq_marked(blocks):
    """Blog body for rendering: '## ' headings ending in '?' that follow a 'Frequently asked questions' /
    'Gyakran ismételt kérdések' heading become FAQ questions (rendered as a smaller <h3>), until the next
    non-question heading. Same rule as faqMark() in js/main.js. Rendering only: the data (and fingerprints) are unchanged."""
    import re
    out, faq = [], False
    for b in blocks or []:
        b = dict(b)
        if b.get('type') == 'h':
            t = str(b.get('text', '')).rstrip()
            if re.match(FAQ_RE, t, re.I):
                faq = True
            elif faq and t.endswith('?'):
                b['type'] = 'q'
            else:
                faq = False
        out.append(b)
    return out


@register.filter
def linkify(text):
    """Escape a paragraph, then turn [label](url) and bare http(s) URLs into links. Only http(s) URLs and root-relative
    paths are linked; external links open in a new tab with rel=noopener. Must match linkify() in js/main.js."""
    import re
    from django.utils.html import escape
    from django.utils.safestring import mark_safe
    out, pos = [], 0
    pat = re.compile(r'\[([^\]\n]{1,200})\]\(((?:https?://|/)[^\s()<>"]*)\)|(https?://[^\s<>"]+[^\s<>".,;:!?)])')
    for m in pat.finditer(str(text)):
        out.append(escape(text[pos:m.start()]))
        label, url = (m.group(1), m.group(2)) if m.group(2) else (m.group(3), m.group(3))
        ext = url.startswith('http') and not url.startswith('https://www.infinitecare.hu')
        out.append('<a href="%s"%s>%s</a>' % (escape(url), ' target="_blank" rel="noopener"' if ext else '', escape(label)))
        pos = m.end()
    out.append(escape(text[pos:]))
    return mark_safe(''.join(out))
