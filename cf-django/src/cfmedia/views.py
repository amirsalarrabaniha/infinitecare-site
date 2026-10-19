from django.http import HttpResponse, HttpResponseRedirect

from .models import StoredFile


def serve_media(request, name):
    f = StoredFile.objects.filter(name=name).first()
    if f is None:
        return HttpResponseRedirect("/static/assets/media/" + name)
    r = HttpResponse(bytes(f.content), content_type=f.content_type)
    r["Cache-Control"] = "public, max-age=3600"
    return r
