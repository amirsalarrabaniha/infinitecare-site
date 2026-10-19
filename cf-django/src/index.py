import os

from workers import DurableObject, WorkerEntrypoint
from django_cf import DjangoCFDurableObject

_SECRETS = ("SECRET_KEY", "MGMT_TOKEN", "ALLOWED_HOSTS", "CSRF_TRUSTED_ORIGINS", "CORS_ALLOWED_ORIGINS")
_app = None


def _get_application(env):
    global _app
    if _app is None:
        for k in _SECRETS:  # expose Worker vars/secrets to Django settings
            v = getattr(env, k, None)
            if v is not None:
                os.environ[k] = str(v)
        from app.wsgi import application
        _app = application
    return _app


class DjangoDO(DjangoCFDurableObject, DurableObject):
    def get_app(self):
        return _get_application(self.env)


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # Single Durable Object instance = single SQLite database for the whole site
        stub = self.env.DO_STORAGE.get(self.env.DO_STORAGE.idFromName("infinitecare"))
        return await stub.fetch(request)
