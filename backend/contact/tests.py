import json
from unittest import mock

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings

from .models import ContactMessage

URL = '/api/contact/'
VALID = {'name': 'Teszt Elek', 'email': 'teszt@example.com', 'phone': '+36 30 123 4567',
         'message': 'Szeretnék időpontot foglalni.', 'lang': 'hu', 'website': ''}


class ContactApiTests(TestCase):
    def setUp(self):
        cache.clear()

    def post(self, data, **kw):
        return self.client.post(URL, json.dumps(data), content_type='application/json', **kw)

    def test_valid_message_is_stored(self):
        r = self.post(VALID)
        self.assertEqual(r.status_code, 201)
        self.assertTrue(r.json()['ok'])
        m = ContactMessage.objects.get()
        self.assertEqual((m.name, m.email, m.language, m.is_read), ('Teszt Elek', 'teszt@example.com', 'hu', False))

    def test_validation_errors(self):
        r = self.post({'name': 'x', 'email': 'nope', 'message': 'hi', 'phone': 'abc'})
        self.assertEqual(r.status_code, 422)
        self.assertEqual(set(r.json()['errors']), {'name', 'email', 'message', 'phone'})
        self.assertFalse(ContactMessage.objects.exists())

    def test_invalid_json(self):
        r = self.client.post(URL, '{bad', content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_honeypot_silently_dropped(self):
        r = self.post({**VALID, 'website': 'http://spam.example'})
        self.assertEqual(r.status_code, 201)
        self.assertFalse(ContactMessage.objects.exists())

    def test_unknown_language_defaults_to_en(self):
        self.post({**VALID, 'lang': 'xx'})
        self.assertEqual(ContactMessage.objects.get().language, 'en')

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(URL).status_code, 405)

    @override_settings(CONTACT_RATE_LIMIT=3)
    def test_rate_limit(self):
        codes = [self.post(VALID).status_code for _ in range(4)]
        self.assertEqual(codes, [201, 201, 201, 429])
        self.assertEqual(ContactMessage.objects.count(), 3)

    @override_settings(NOTIFY_EMAIL='owner@example.com', EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_notification_email(self):
        self.post(VALID)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Teszt Elek', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['owner@example.com'])

    @override_settings(NOTIFY_EMAIL='')
    def test_works_without_email(self):
        self.assertEqual(self.post(VALID).status_code, 201)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(NOTIFY_EMAIL='owner@example.com')
    def test_smtp_failure_does_not_lose_message(self):
        with mock.patch('contact.views.send_mail', side_effect=OSError('smtp down')):
            self.assertEqual(self.post(VALID).status_code, 201)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_cors_header_for_github_pages(self):
        r = self.post(VALID, HTTP_ORIGIN='https://amirsalarrabaniha.github.io')
        self.assertEqual(r['Access-Control-Allow-Origin'], 'https://amirsalarrabaniha.github.io')
        r = self.post(VALID, HTTP_ORIGIN='https://evil.example')
        self.assertNotIn('Access-Control-Allow-Origin', r)

    def test_admin_lists_messages(self):
        from django.contrib.auth.models import User
        User.objects.create_superuser('admin', 'a@example.com', 'pw-12345-xyz')
        self.post(VALID)
        self.client.login(username='admin', password='pw-12345-xyz')
        r = self.client.get('/admin/contact/contactmessage/')
        self.assertContains(r, 'Teszt Elek')
