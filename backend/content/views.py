import json

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from . import data
from .ui import UI

LANGS = settings.SITE_LANGUAGES


def page_context(lang, page, urls, api_url):
    other = 'hu' if lang == 'en' else 'en'
    ui = UI[lang]
    nav_keys = ['index', 'services', 'prices']
    nav = [dict(key=k, label=ui['nav'][i], href=urls.page(k)) for i, k in enumerate(nav_keys)]
    nav.append(dict(key='offers', label=ui['nav'][3], href=urls.page('services') + '#packages'))
    ctx = dict(lang=lang, other=other, page=page, ui=ui, title=ui['titles'][page], nav=nav, S=urls.static,
               urls={k: urls.page(k) for k in nav_keys},
               switch={l: urls.page(page, l) for l in LANGS},
               alternates={l: settings.STATIC_EXPORT_SITE_URL + ('' if l == 'en' else 'hu/') + f'{page}.html' for l in LANGS},
               site=data.site_settings(lang), api_url=api_url)
    if page == 'index':
        ctx.update(home=data.home(lang, urls), counters=data.counters(lang))
    elif page == 'services':
        svcs = data.services(lang, urls)
        ctx.update(services_before=svcs[:5], services_after=svcs[5:], packages=data.packages(lang, urls),
                   hero_image=urls.static + 'assets/images/services.jpg')
    else:
        ctx.update(categories=data.prices(lang), hero_image=urls.static + 'assets/images/prices.jpg')
    return ctx


def root(request):
    pref = request.COOKIES.get('ic-lang')
    return redirect(f'/{pref if pref in LANGS else "en"}/')


def page(request, lang, name='index'):
    if lang not in LANGS or name not in data.PAGES:
        raise Http404
    ctx = page_context(lang, name, data.LiveUrls(lang), '/api/contact/')
    return render(request, f'site/{name}.html', ctx)


def legacy(request, name):  # old static URLs like /services.html, /hu/prices.html
    return redirect(f'/{request.path.startswith("/hu/") and "hu" or "en"}/{"" if name == "index" else name + "/"}', permanent=True)


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
def api_prices(request):
    return _json({'results': data.prices(_lang(request))})


class _AbsUrls(data.LiveUrls):
    def __init__(self, request, lang):
        super().__init__(lang)
        self.request = request

    def media(self, f):
        return self.request.build_absolute_uri(f.url) if f else ''
