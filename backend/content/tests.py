import pathlib
import tempfile

from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import BlogPost, GalleryItem, HomePage, PriceItem, Service, SiteSettings, VideoClip

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

    def test_social_links_everywhere(self):
        urls = ['https://www.youtube.com/@InfiniteCareBeautyClinic', 'https://www.instagram.com/infinitecarebeauty/',
                'https://vm.tiktok.com/ZN8DVD2M3/']
        for path in ('/en/', '/hu/', '/en/services/', '/hu/prices/', '/en/blog/', '/hu/blog/'):
            html = self.client.get(path).content.decode()
            for u in urls:
                self.assertIn(f'href="{u}" target="_blank" rel="noopener noreferrer me"', html, (path, u))
        home = self.client.get('/hu/').content.decode()
        self.assertEqual(home.count('rel="noopener noreferrer me"'), 8)   # footer + contact section, 4 networks each
        self.assertIn('aria-label="Infinite Care – TikTok (új lapon nyílik meg)"', home)
        self.assertIn('aria-label="Infinite Care on YouTube (opens in a new tab)"', self.client.get('/en/').content.decode())
        self.assertIn('"sameAs": ["https://www.facebook.com/', home)
        self.assertEqual(self.client.get('/api/settings/').json()['tiktok'], urls[2])

    def test_social_links_editable(self):
        s = SiteSettings.load()
        s.tiktok = ''
        s.youtube = 'https://www.youtube.com/@other'
        s.save()
        html = self.client.get('/en/').content.decode()
        self.assertNotIn('tiktok.com', html)
        self.assertIn('https://www.youtube.com/@other', html)

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
        p = pathlib.Path(out)
        hu = (p / 'hu' / 'services.html').read_text(encoding='utf-8')
        self.assertIn('href="../services.html" hreflang="en"', hu)
        self.assertIn('src="../assets/media/services/', hu)
        self.assertIn('href="../css/style.css?v=', hu)
        en = (p / 'index.html').read_text(encoding='utf-8')
        self.assertIn('href="hu/index.html" hreflang="hu"', en)
        self.assertTrue((p / 'assets' / 'media' / 'services').is_dir())

    # ---- clinic photo gallery / reels ----
    def test_gallery_and_reels_seeded_and_rendered(self):
        self.assertEqual(GalleryItem.objects.count(), 13)
        self.assertEqual(VideoClip.objects.count(), 2)
        for lang, word in [('en', 'The entrance of Infinite Care'), ('hu', 'Az Infinite Care Beauty Clinic bejárata')]:
            r = self.client.get(f'/{lang}/')
            self.assertContains(r, 'id="gallery"')
            self.assertContains(r, 'data-reel')
            self.assertContains(r, word)
        r = self.client.get('/api/gallery/?lang=hu').json()
        self.assertEqual((len(r['photos']), len(r['videos'])), (13, 2))
        self.assertTrue(r['photos'][0]['image'].startswith('http://testserver/media/gallery/'))

    # ---- blog ----
    def test_blog_seed(self):
        self.assertEqual(BlogPost.objects.count(), 3)
        self.assertTrue(all(p.title_hu and p.body_hu and p.cover for p in BlogPost.objects.all()))

    def test_blog_list_and_detail_both_languages(self):
        r = self.client.get('/en/blog/')
        self.assertContains(r, 'Professional teeth whitening: the basics')
        self.assertContains(r, 'href="/en/blog/what-to-expect-at-your-first-visit/"')
        r = self.client.get('/hu/blog/')
        self.assertContains(r, 'Professzionális fogfehérítés')
        self.assertContains(r, 'href="/hu/blog/laser-hair-removal-preparation-and-aftercare/"')
        r = self.client.get('/hu/blog/laser-hair-removal-preparation-and-aftercare/')
        self.assertContains(r, 'Lézeres szőrtelenítés: felkészülés és utógondozás')
        self.assertContains(r, 'hreflang="en" href="https://amirsalarrabaniha.github.io/infinitecare-site/blog/laser-hair-removal-preparation-and-aftercare.html"')
        self.assertContains(r, 'href="/en/blog/laser-hair-removal-preparation-and-aftercare/" hreflang="en"')
        self.assertContains(r, 'property="og:image"')
        self.assertContains(r, '"@type": "BlogPosting"')
        self.assertContains(self.client.get('/en/blog/professional-teeth-whitening-basics/'), '<h2>What to keep in mind</h2>')

    def test_blog_nav_and_footer_links_everywhere(self):
        for lang, label in [('en', 'Blog'), ('hu', 'Blog')]:
            for path in ['', 'services/', 'prices/', 'blog/']:
                r = self.client.get(f'/{lang}/{path}')
                self.assertContains(r, f'<a href="/{lang}/blog/" class="')
                self.assertContains(r, f'<a href="/{lang}/blog/">{label}</a>')

    def test_unpublished_post_is_hidden(self):
        p = BlogPost.objects.get(slug='professional-teeth-whitening-basics')
        p.is_published = False
        p.save()
        self.assertNotContains(self.client.get('/en/blog/'), 'teeth whitening')
        self.assertEqual(self.client.get('/en/blog/professional-teeth-whitening-basics/').status_code, 404)
        self.assertEqual(self.client.get('/api/blog/professional-teeth-whitening-basics/').status_code, 404)
        self.assertEqual(self.client.get('/xx/blog/professional-teeth-whitening-basics/').status_code, 404)

    def test_hungarian_falls_back_to_english(self):
        p = BlogPost.objects.get(slug='professional-teeth-whitening-basics')
        p.title_hu = p.body_hu = ''
        p.save()
        self.assertContains(self.client.get('/hu/blog/professional-teeth-whitening-basics/'), 'Professional teeth whitening: the basics')

    def test_blog_markup_is_escaped(self):
        BlogPost.objects.create(slug='x', title_en='T <b>', excerpt_en='e', body_en='## H\n\n<script>alert(1)</script>\n\n- a\n- b', cover='blog/x.webp')
        r = self.client.get('/en/blog/x/')
        self.assertNotContains(r, '<script>alert(1)</script>')
        self.assertContains(r, '<ul><li>a</li><li>b</li></ul>')

    def test_blog_api(self):
        r = self.client.get('/api/blog/?lang=hu').json()['results']
        self.assertEqual(len(r), 3)
        self.assertEqual(r[0]['slug'], 'professional-teeth-whitening-basics')   # newest first
        self.assertTrue(r[0]['cover'].startswith('http://testserver/media/blog/'))
        d = self.client.get('/api/blog/professional-teeth-whitening-basics/?lang=en').json()
        self.assertEqual(d['title'], 'Professional teeth whitening: the basics')
        self.assertIn('blocks', d)

    def test_legacy_blog_html_redirects(self):
        self.assertRedirects(self.client.get('/hu/blog/professional-teeth-whitening-basics.html'),
                             '/hu/blog/professional-teeth-whitening-basics/', status_code=301, fetch_redirect_response=False)
        self.assertRedirects(self.client.get('/blog.html'), '/en/blog/', status_code=301, fetch_redirect_response=False)

    def test_static_export_performance_and_discovery(self):
        out = tempfile.mkdtemp()
        call_command('export_static', out=out, api_url='/api/contact/', site_url='https://example.test/', clean_urls=True, verbosity=0)
        p = pathlib.Path(out)
        en = (p / 'index.html').read_text(encoding='utf-8')
        self.assertNotIn('fonts.googleapis.com', en)
        self.assertIn('rel="preload" href="assets/fonts/montserrat-latin.woff2"', en)
        self.assertRegex(en, r'<img src="assets/media/home/[^"]+" alt="" width="\d+" height="\d+" fetchpriority="high"')  # LCP image
        self.assertIn('width="248" height="260"', en)                                  # logos are sized
        self.assertNotIn('<iframe', en)                                                 # Google Maps only after a click
        self.assertIn('data-map="https://www.google.com/maps/embed', en)
        self.assertIn('toolname="send_message"', en)
        self.assertIn('<link rel="canonical" href="https://example.test/">', en)
        self.assertIn('<link rel="canonical" href="https://example.test/hu/services">', (p / 'hu' / 'services.html').read_text(encoding='utf-8'))
        self.assertIn('Térkép megjelenítése', (p / 'hu' / 'index.html').read_text(encoding='utf-8'))
        self.assertNotIn('<h4', en)
        sm = (p / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertIn('<loc>https://example.test/hu/blog</loc>', sm)
        self.assertEqual(sm.count('<loc>'), 2 * (4 + BlogPost.objects.filter(is_published=True).count()))
        self.assertIn('Sitemap: https://example.test/sitemap.xml', (p / 'robots.txt').read_text(encoding='utf-8'))
        llms = (p / 'llms.txt').read_text(encoding='utf-8')
        self.assertTrue(llms.startswith('# Infinite Care Beauty Clinic'))
        self.assertIn('](https://example.test/services)', llms)
        # shipped as static assets and cache/security headers are not excluded from the deploy
        root = pathlib.Path(__file__).resolve().parents[2]
        ignore = (root / '.assetsignore').read_text().split()
        self.assertTrue((root / '_headers').is_file())
        self.assertNotIn('_headers', ignore)
        self.assertIn('Content-Security-Policy', (root / '_headers').read_text())
        for f in ('montserrat-latin', 'playfair-display-latin', 'mr-dafoe-latin'):
            self.assertTrue((root / 'assets' / 'fonts' / f'{f}.woff2').is_file(), f)

    def test_static_export_blog(self):
        out = tempfile.mkdtemp()
        call_command('export_static', out=out, api_url='', verbosity=0)
        p = pathlib.Path(out)
        slug = 'laser-hair-removal-preparation-and-aftercare'
        for f in ['blog.html', f'blog/{slug}.html', 'hu/blog.html', f'hu/blog/{slug}.html']:
            self.assertTrue((p / f).is_file(), f)
        en = (p / 'blog' / f'{slug}.html').read_text(encoding='utf-8')
        self.assertIn('href="../css/style.css?v=', en)
        self.assertIn('src="../assets/media/blog/', en)
        self.assertIn(f'href="../hu/blog/{slug}.html" hreflang="hu"', en)
        self.assertIn('href="../blog.html">Blog</a>', en)
        hu = (p / 'hu' / 'blog' / f'{slug}.html').read_text(encoding='utf-8')
        self.assertIn('href="../../css/style.css?v=', hu)
        self.assertIn(f'href="../../blog/{slug}.html" hreflang="en"', hu)
        self.assertIn('src="../../assets/media/blog/', hu)
        self.assertIn('href="../index.html" class="brand"', hu)
        lst = (p / 'hu' / 'blog.html').read_text(encoding='utf-8')
        self.assertIn(f'href="blog/{slug}.html"', lst)
        self.assertIn('src="../assets/media/blog/', lst)
        self.assertIn('href="../blog.html" hreflang="en"', lst)
        self.assertIn('href="blog.html">Blog</a>', (p / 'hu' / 'index.html').read_text(encoding='utf-8'))
        # unpublished posts disappear on the next export
        BlogPost.objects.filter(slug=slug).update(is_published=False)
        call_command('export_static', out=out, api_url='', verbosity=0)
        self.assertFalse((p / 'blog' / f'{slug}.html').exists())
