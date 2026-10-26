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
