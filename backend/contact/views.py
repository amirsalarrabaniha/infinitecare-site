import json
import logging
import re

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import ContactMessage

log = logging.getLogger(__name__)
PHONE_RE = re.compile(r'^[+0-9 ()/.-]{5,40}$')


def client_ip(request):
    if getattr(settings, 'TRUST_CF_CONNECTING_IP', False) and request.META.get('HTTP_CF_CONNECTING_IP'):
        return request.META['HTTP_CF_CONNECTING_IP']
    if settings.TRUST_X_FORWARDED_FOR and request.META.get('HTTP_X_FORWARDED_FOR'):
        return request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def rate_limited(ip):
    key = f'contact-rl:{ip}'
    cache.add(key, 0, settings.CONTACT_RATE_WINDOW)
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, settings.CONTACT_RATE_WINDOW)
        count = 1
    return count > settings.CONTACT_RATE_LIMIT


@csrf_exempt  # public JSON endpoint (also called cross-origin from GitHub Pages); protected by validation, honeypot and rate limit
@require_POST
def contact(request):
    ip = client_ip(request)
    if rate_limited(ip):
        return JsonResponse({'ok': False, 'error': 'rate_limited'}, status=429)
    try:
        data = json.loads(request.body or b'{}') if 'json' in request.content_type else request.POST.dict()
        if not isinstance(data, dict):
            raise ValueError
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'invalid_json'}, status=400)

    s = lambda k, n: (data.get(k) or '').strip()[:n] if isinstance(data.get(k, ''), str) else ''
    if s('website', 200):  # honeypot filled -> bot. Pretend success, store nothing.
        return JsonResponse({'ok': True}, status=201)

    fields = dict(name=s('name', 100), email=s('email', 200), phone=s('phone', 40), message=s('message', 5000),
                  language=s('lang', 2) if s('lang', 2) in ('en', 'hu') else 'en')
    errors = {}
    if len(fields['name']) < 2:
        errors['name'] = 'required'
    try:
        validate_email(fields['email'])
    except ValidationError:
        errors['email'] = 'invalid'
    if len(fields['message']) < 5:
        errors['message'] = 'too_short'
    if fields['phone'] and not PHONE_RE.match(fields['phone']):
        errors['phone'] = 'invalid'
    if errors:
        return JsonResponse({'ok': False, 'errors': errors}, status=422)

    msg = ContactMessage.objects.create(ip_address=ip, **fields)
    if settings.NOTIFY_EMAIL:
        try:
            send_mail(f'New website message from {msg.name}',
                      f'Name: {msg.name}\nE-mail: {msg.email}\nPhone: {msg.phone or "-"}\nLanguage: {msg.language}\n\n{msg.message}',
                      settings.DEFAULT_FROM_EMAIL, [settings.NOTIFY_EMAIL], fail_silently=False)
        except Exception:  # never lose the message because of SMTP problems
            log.exception('Contact notification e-mail failed')
    return JsonResponse({'ok': True, 'id': msg.id}, status=201)
