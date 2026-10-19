import json

from django.http import HttpResponse
from django.template import Context, Engine
from django.views.i18n import JavaScriptCatalog

from .i18n_js import TEMPLATE


class BundledJavaScriptCatalog(JavaScriptCatalog):
    def render_to_response(self, context, **kwargs):
        indent = lambda s: s.replace("\n", "\n  ")
        context["catalog_str"] = indent(json.dumps(context["catalog"], sort_keys=True, indent=2)) if context["catalog"] else None
        context["formats_str"] = indent(json.dumps(context["formats"], sort_keys=True, indent=2))
        return HttpResponse(Engine().from_string(TEMPLATE).render(Context(context)), 'text/javascript; charset="utf-8"')
