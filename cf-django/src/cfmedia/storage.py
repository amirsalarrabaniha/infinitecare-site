import mimetypes

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class DatabaseStorage(Storage):
    """Stores uploaded files in the database (Durable Object SQLite). URL: /media/<name>.
    Files that are not in the DB (seeded content) are redirected to the static copy in /static/assets/media/."""

    def _model(self):
        from .models import StoredFile
        return StoredFile

    def _open(self, name, mode="rb"):
        return ContentFile(bytes(self._model().objects.get(name=name).content), name=name)

    def _save(self, name, content):
        data = content.read()
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        self._model().objects.update_or_create(name=name, defaults={"content": data, "content_type": ctype, "size": len(data)})
        return name

    def exists(self, name):
        return self._model().objects.filter(name=name).exists()

    def delete(self, name):
        self._model().objects.filter(name=name).delete()

    def size(self, name):
        return self._model().objects.get(name=name).size

    def url(self, name):
        return "/media/" + name

    def listdir(self, path):
        return [], list(self._model().objects.filter(name__startswith=path).values_list("name", flat=True))
