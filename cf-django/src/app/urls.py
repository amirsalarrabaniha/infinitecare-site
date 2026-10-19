import hmac
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from config_urls import urlpatterns as site_urlpatterns
from cfmedia.views import serve_media
from app.jsi18n import BundledJavaScriptCatalog


@csrf_exempt
@require_POST
def manage(request, command):
    """Token-protected management endpoint: migrate, load_initial_content, create/reset superuser."""
    token = request.headers.get("X-Mgmt-Token", "")
    if not settings.MGMT_TOKEN or not hmac.compare_digest(token, settings.MGMT_TOKEN):
        return JsonResponse({"ok": False}, status=403)
    try:
        if command == "migrate":
            call_command("migrate", interactive=False, verbosity=0)
        elif command == "load_initial_content":
            call_command("load_initial_content", force=request.GET.get("force") == "1")
        elif command == "superuser":
            body = json.loads(request.body)
            User = get_user_model()
            u, _ = User.objects.get_or_create(username=body["username"], defaults={"email": body.get("email", "")})
            u.is_staff = u.is_superuser = True
            u.set_password(body["password"])
            u.save()
        else:
            return JsonResponse({"ok": False, "error": "unknown command"}, status=404)
        return JsonResponse({"ok": True, "command": command})
    except Exception as e:
        return JsonResponse({"ok": False, "error": f"{type(e).__name__}: {e}"}, status=500)


def health(request):
    return JsonResponse({"ok": True})


urlpatterns = [
    path("__manage__/<str:command>/", manage),
    path("admin/jsi18n/", BundledJavaScriptCatalog.as_view(packages=["django.contrib.admin"])),
    path("health", health),
    path("media/<path:name>", serve_media),
] + [p for p in site_urlpatterns if "media" not in str(p.pattern)]
