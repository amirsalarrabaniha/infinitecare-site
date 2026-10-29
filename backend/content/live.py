"""Fingerprints for the runtime ("live") update of the static pages (see js/main.js, README "Live content").

Every part of a page that the browser may re-render from the JSON API carries `data-fp="<fingerprint of its data>"`.
main.js fetches the API, fingerprints the same slice of data the same way, and only touches the DOM when they differ.
The two implementations (here and `fp()` in js/main.js) must stay identical:
  canonical JSON (sorted keys, ASCII only, no spaces) of the data, media URLs reduced to `~/<name>`, FNV-1a (32 bit) over
  the characters, written as `<hex>-<length>`.
"""
import json
import re

_MEDIA = re.compile(r'^(?:\.\./)*assets/media/(.+)$')
FNV_OFFSET, FNV_PRIME = 0x811c9dc5, 0x01000193


def _canon(o):
    if isinstance(o, str):
        m = _MEDIA.match(o)
        return '~/' + m.group(1) if m else str(o)
    if isinstance(o, (list, tuple)):
        return [_canon(x) for x in o]
    if isinstance(o, dict):
        return {k: _canon(v) for k, v in o.items()}
    return o


def fp(o):
    s = json.dumps(_canon(o), sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    h = FNV_OFFSET
    for ch in s:  # ASCII only, so one char = one byte
        h = ((h ^ ord(ch)) * FNV_PRIME) & 0xffffffff
    return f'{h:x}-{len(s)}'


def no_url(items):
    """Blog items without the site-relative `url` (it differs between the API and the static layout)."""
    return [{k: v for k, v in p.items() if k != 'url'} for p in items]


def index_fps(h, counters, gallery, yt, clips):
    return dict(
        hero=fp([h['hero_image'], h['hello'], h['h1_main'], h['h1_em'], h['lead']]),
        marquee=fp(h['marquee']), f1=fp(h['f1']), f2=fp(h['f2']), counters=fp(counters),
        cta=fp([h['cta_image'], h['cta_script'], h['cta_title'], h['cta_button']]),
        contact=fp([h['contact_eyebrow'], h['contact_title'], h['contact_text'], h['contact_image']]),
        gallery=fp(dict(photos=gallery, yt=yt, clips=clips)))


def svc_fp(s):
    """The live part of a service page: lead text, body and videos."""
    return fp([s['description'], s['blocks'], s['videos']])
