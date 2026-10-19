import tempfile

from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Service, PriceItem, SiteSettings, HomePage

TMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class ContentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('load_initial_content', verbosity=0)

    def test_seed(self):
        self.assertEqual(Service.objects.count(), 11)
        self.assertEqual(PriceItem.objects.count(), 63)
        self.assertEqual(SiteSettings.load().phone, '+36 1 707 0075')

    def test_pages_both_languages(self):
        for lang, word in [('en', 'Hello Beautiful!'), ('hu', 'Budapest legújabb esztétikai klinikája')]:
            r = self.client.get(f'/{lang}/')
            self.assertContains(r, word)
            self.assertContains(r, f'<html lang="{lang}">')
        self.assertContains(self.client.get('/hu/services/'), 'Exoszóma Terápia')
        self.assertContains(self.client.get('/en/prices/'), '70.000 HUF')
        self.assertContains(self.client.get('/hu/prices/'), '70.000 Ft')

    def test_language_switch_links_point_to_same_page(self):
        r = self.client.get('/en/prices/')
        self.assertContains(r, 'href="/hu/prices/" hreflang="hu"')
        r = self.client.get('/hu/services/')
        self.assertContains(r, 'href="/en/services/" hreflang="en"')

    def test_unknown_language_404(self):
        self.assertEqual(self.client.get('/de/').status_code, 404)

    def test_root_redirect_uses_cookie(self):
        self.assertRedirects(self.client.get('/'), '/en/')
        self.client.cookies['ic-lang'] = 'hu'
        self.assertRedirects(self.client.get('/'), '/hu/')

    def test_db_edit_shows_on_site(self):
        s = Service.objects.get(title_en='Brazilift')
        s.title_hu = 'Brazil popsi emelés'
        s.save()
        self.assertContains(self.client.get('/hu/services/'), 'Brazil popsi emelés')
        s.is_active = False
        s.save()
        self.assertNotContains(self.client.get('/en/services/'), 'Brazilift')

    def test_json_api(self):
        r = self.client.get('/api/services/?lang=hu').json()
        self.assertEqual(r['results'][0]['title'], 'Exoszóma Terápia')
        self.assertTrue(r['results'][0]['image'].startswith('http://testserver/media/services/'))
        self.assertEqual(len(self.client.get('/api/prices/').json()['results']), 10)
        self.assertEqual(self.client.get('/api/packages/?lang=hu').json()['results'][1]['name'], 'Menyasszony')
        self.assertEqual(self.client.get('/api/settings/?lang=hu').json()['address'], 'Bp. VI. Podmaniczky u. 5.')
        self.assertEqual(len(self.client.get('/api/home/').json()['counters']), 4)

    def test_static_export(self):
        out = tempfile.mkdtemp()
        call_command('export_static', out=out, api_url='', verbosity=0)
        import pathlib
        p = pathlib.Path(out)
        hu = (p / 'hu' / 'services.html').read_text(encoding='utf-8')
        self.assertIn('href="../services.html" hreflang="en"', hu)
        self.assertIn('src="../assets/media/services/', hu)
        self.assertIn('href="../css/style.css"', hu)
        en = (p / 'index.html').read_text(encoding='utf-8')
        self.assertIn('href="hu/index.html" hreflang="hu"', en)
        self.assertTrue((p / 'assets' / 'media' / 'services').is_dir())
