import pathlib
import re
import tempfile

from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import BlogPost, GalleryItem, HomePage, Service, SiteSettings, VideoClip, YouTubeVideo

TMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class ContentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('load_initial_content', verbosity=0)

    def test_seed(self):
        self.assertEqual(Service.objects.count(), 10)
        self.assertEqual(SiteSettings.load().phone, '+36 1 707 0075')

    def test_pages_both_languages(self):
        for lang, word in [('en', 'Hello Beautiful!'), ('hu', 'Budapest legújabb esztétikai klinikája')]:
            r = self.client.get(f'/{lang}/')
            self.assertContains(r, word)
            self.assertContains(r, f'<html lang="{lang}">')
        self.assertContains(self.client.get('/hu/services/'), 'Exoszóma Terápia')

    def test_language_switch_links_point_to_same_page(self):
        r = self.client.get('/en/services/')
        self.assertContains(r, 'href="/hu/services/" hreflang="hu"')
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
                'https://www.tiktok.com/@infinitecarebeautyclinic']
        for path in ('/en/', '/hu/', '/en/services/', '/hu/services/', '/en/blog/', '/hu/blog/'):
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
        self.assertEqual(self.client.get('/api/prices/').status_code, 404)
        self.assertEqual(self.client.get('/api/packages/').status_code, 404)
        self.assertEqual(self.client.get('/api/settings/?lang=hu').json()['address'], 'Bp. VI. Podmaniczky u. 5.')
        self.assertEqual(len(self.client.get('/api/home/').json()['counters']), 2)

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

    def test_gallery_treatment_categories(self):
        cats = {g.image.name.split('/')[-1].split('.')[0].split('_')[0]: g.category for g in GalleryItem.objects.all()}
        self.assertEqual(cats['teeth-whitening-before-after'], 'whitening')
        self.assertEqual(cats['treatment-microneedling'], 'facial')
        self.assertEqual(cats['treatment-laser-hair-removal'], 'laser')
        self.assertEqual(cats['treatment-emsculpt'], 'emsculpt')
        self.assertEqual(set(VideoClip.objects.values_list('category', flat=True)), {'facial'})
        for lang, labels in [('en', ['All', 'Clinic', 'Treatments', 'Events', 'Teeth Whitening', 'Facial', 'Laser', 'Emsculpt', 'Carbon Peeling', 'Cellulite', 'Brazilift']),
                             ('hu', ['Mind', 'Klinika', 'Kezelések', 'Események', 'Fogfehérítés', 'Arckezelés', 'Lézer', 'Emsculpt', 'Carbon hámlasztás', 'Cellulit', 'Brazilift'])]:
            html = self.client.get(f'/{lang}/').content.decode()
            tabs = re.findall(r'data-filter="([a-z]+)"[^>]*>([^<]+)</button>', html)
            self.assertEqual([t[1] for t in tabs], labels)
            for key, _ in tabs[1:]:   # no tab is empty; specific treatments also show under "Treatments"
                self.assertTrue(re.search(r'data-cat="[^"]*\b%s\b' % key, html), key)
        self.assertRegex(html, r'data-cat="whitening treatments"')
        self.assertRegex(html, r'data-cat="events"')
        self.assertIn('role="status"', html)
        r = self.client.get('/api/gallery/').json()
        self.assertEqual({p['category'] for p in r['photos']} >= {'whitening', 'facial', 'laser', 'emsculpt'}, True)
        self.assertEqual({v['category'] for v in r['videos']}, {'facial'})

    def test_load_clinic_media_recategorises_existing_items(self):
        GalleryItem.objects.exclude(category__in=['clinic', 'events']).update(category='treatments')
        VideoClip.objects.update(category='treatments')
        call_command('load_clinic_media', verbosity=0)
        self.assertEqual(sorted(GalleryItem.objects.filter(category__in=['whitening', 'facial', 'laser', 'emsculpt']).values_list('category', flat=True)),
                         ['emsculpt', 'facial', 'laser', 'whitening'])
        self.assertEqual(set(VideoClip.objects.values_list('category', flat=True)), {'facial'})

    def test_empty_gallery_category_has_no_tab(self):
        GalleryItem.objects.filter(category='laser').delete()
        self.assertIn('data-filter="laser"', self.client.get('/en/').content.decode())   # the laser videos still fill the tab
        YouTubeVideo.objects.filter(category='laser').delete()
        html = self.client.get('/en/').content.decode()
        self.assertNotIn('data-filter="laser"', html)
        self.assertIn('data-filter="facial"', html)

    # ---- YouTube videos ----

    def test_youtube_seed_and_placements(self):
        self.assertEqual(YouTubeVideo.objects.count(), 11)
        ids = lambda html: re.findall(r'data-yt="([\w-]{11})"', html)
        en, hu = self.client.get('/en/').content.decode(), self.client.get('/hu/').content.decode()
        self.assertIn('TXip__AECX0', ids(en))                                   # featured welcome film
        self.assertIn('ckGJs4jgLhI', ids(en)); self.assertNotIn('Miej6lMfoRk', ids(en))   # language variants
        self.assertIn('Miej6lMfoRk', ids(hu)); self.assertNotIn('ckGJs4jgLhI', ids(hu))
        self.assertIn('xr3tZAVtGsA', ids(en)); self.assertIn('GFkCHCBCbmU', ids(hu))
        self.assertIn('Dt0dmmsswzc', ids(en)); self.assertIn('Dt0dmmsswzc', ids(hu))     # laser FAQ in the Laser category
        self.assertRegex(en, r'class="g-item g-vid reveal" data-cat="laser treatments"')
        self.assertIn('https://www.youtube.com/@InfiniteCareBeautyClinic', en)    # subscribe link
        # nothing from YouTube is loaded until a click: no iframe / third-party URL in the HTML, posters are our own files
        self.assertNotIn('<iframe', en)
        self.assertNotRegex(en, r'src="https?://[^"]*(youtube|ytimg)')
        self.assertIn('/media/youtube/', en)
        svc = self.client.get('/en/services/').content.decode()
        self.assertEqual(set(ids(svc)), {'ckGJs4jgLhI', 'xr3tZAVtGsA', 'RhWkw_mH0M8', 'HcqKo_QBSBo', 'otZDPSVBzZ8', 'jEYC7rDP6W8'})
        post = self.client.get('/en/blog/laser-hair-removal-preparation-and-aftercare/').content.decode()
        self.assertEqual(ids(post), ['Dt0dmmsswzc'])
        self.assertEqual(ids(self.client.get('/hu/blog/professional-teeth-whitening-basics/').content.decode()), ['Miej6lMfoRk'])

    def test_youtube_inactive_and_api(self):
        YouTubeVideo.objects.filter(youtube_id='TXip__AECX0').update(is_active=False)
        self.assertNotIn('TXip__AECX0', self.client.get('/en/').content.decode())
        r = self.client.get('/api/gallery/?lang=hu').json()['youtube']
        self.assertEqual(len(r), 8)   # 11 minus the inactive one minus the two English-only variants (whitening, laser)
        v = next(x for x in r if x['youtube_id'] == 'RhWkw_mH0M8')
        self.assertEqual((v['title'], v['category'], v['vertical'], v['width'], v['height']), ('Emsculpt testkezelés', 'emsculpt', True, 405, 720))

    def test_load_clinic_media_adds_youtube_to_existing_db(self):
        YouTubeVideo.objects.all().delete()
        call_command('load_clinic_media', verbosity=0)
        self.assertEqual(YouTubeVideo.objects.count(), 11)
        call_command('load_clinic_media', verbosity=0)   # idempotent
        self.assertEqual(YouTubeVideo.objects.count(), 11)

    def test_csp_allows_only_youtube_nocookie_frames(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        csp = next(l for l in (root / '_headers').read_text().splitlines() if 'Content-Security-Policy' in l)
        self.assertIn('frame-src https://www.google.com https://maps.google.com https://www.youtube-nocookie.com;', csp)
        self.assertIn("script-src 'self';", csp)

    # ---- online booking ----

    def test_booking_links_everywhere(self):
        url = 'https://l.fresha.com/3dvz3n7j6'
        self.assertEqual(SiteSettings.load().booking_url, url)
        self.assertEqual(self.client.get('/api/settings/').json()['booking_url'], url)
        link = f'href="{url}" target="_blank" rel="noopener noreferrer"'
        for path, n in [('/en/', 4), ('/hu/', 4), ('/en/services/', 13), ('/hu/services/', 13), ('/en/blog/', 2),
                        ('/en/blog/laser-hair-removal-preparation-and-aftercare/', 3)]:
            html = self.client.get(path).content.decode()
            self.assertGreaterEqual(html.count(link), n, path)
            self.assertIn('nav-cta', html)
        en, hu = self.client.get('/en/').content.decode(), self.client.get('/hu/').content.decode()
        self.assertIn('Book online', en); self.assertIn('Book now', en)
        self.assertIn('Online időpontfoglalás', hu); self.assertIn('>Foglalás<', hu)
        self.assertIn('+36 1 707 0075', en)
        self.assertNotIn('fresha.com/a/', en)   # short link only, no iframe / embed
        self.assertNotIn('<iframe', en)
        ld = re.search(r'application/ld\+json">(.*?)</script>', en, re.S).group(1)
        self.assertIn('"ReserveAction"', ld); self.assertIn(url, ld)

    def test_booking_url_editable_and_can_be_hidden(self):
        s = SiteSettings.load()
        s.booking_url = 'https://example.com/book'
        s.save()
        self.assertContains(self.client.get('/en/'), 'href="https://example.com/book" target="_blank"')
        s.booking_url = ''
        s.save()
        html = self.client.get('/en/').content.decode()
        self.assertNotIn('Book online', html); self.assertNotIn('ReserveAction', html); self.assertNotIn('3dvz3n7j6', html)
        self.assertIn('class="btn btn-sm nav-cta" href="tel:', html)   # header falls back to the phone button
        call_command('load_clinic_media', update_social=True, verbosity=0)
        self.assertEqual(SiteSettings.load().booking_url, 'https://l.fresha.com/3dvz3n7j6')

    # ---- removed Offers/packages section; header "Offers" is an external Fresha link ----

    OFFERS = 'https://l.fresha.com/3yv8307j6'

    def test_offers_header_link_is_external_fresha(self):
        for lang, label in [('en', 'Offers'), ('hu', 'Akciók')]:
            for path in ['', 'services/', 'blog/']:
                html = self.client.get(f'/{lang}/{path}').content.decode()
                self.assertEqual(html.count(f'href="{self.OFFERS}"'), 1, (lang, path))
                self.assertIn(f'<a href="{self.OFFERS}" class="" target="_blank" rel="noopener noreferrer" data-s="offers">{label}', html)
                # the "Book now" buttons keep the original booking URL
                self.assertIn('href="https://l.fresha.com/3dvz3n7j6" target="_blank" rel="noopener noreferrer"', html)
                self.assertNotIn('#packages', html)
                self.assertNotIn('id="packages"', html)
                self.assertNotIn('class="pk', html)

    def test_offers_link_hidden_when_setting_empty(self):
        ss = SiteSettings.load()
        ss.offers_url = ''
        ss.save()
        self.assertNotContains(self.client.get('/en/'), 'Offers</a>')

    def test_packages_are_gone(self):
        self.assertEqual(self.client.get('/api/packages/').status_code, 404)
        html = self.client.get('/en/services/').content.decode()
        for w in ('309 000', 'Bridal', 'popular packages'):
            self.assertNotIn(w, html)
        self.assertNotContains(self.client.get('/hu/'), 'csomag')

    def test_static_export_has_no_offers_section(self):
        out = tempfile.mkdtemp()
        call_command('export_static', out=out, api_url='', verbosity=0, site_url='https://example.com/', clean_urls=True)
        for f in ('sitemap.xml', 'llms.txt', 'index.html', 'hu/index.html', 'services.html', 'hu/services.html'):
            txt = (pathlib.Path(out) / f).read_text(encoding='utf-8')
            self.assertNotIn('packages', txt.lower(), f)
            self.assertNotIn('309 000', txt, f)

    # ---- removed sections: massage and prices ----

    def test_massage_and_prices_are_gone(self):
        self.assertFalse(Service.objects.filter(title_en='Massage').exists())
        for lang, words in [('en', ['massage', 'our prices']), ('hu', ['masszázs', 'áraink'])]:
            for path in ['', 'services/', 'blog/', 'blog/laser-hair-removal-preparation-and-aftercare/']:
                html = self.client.get(f'/{lang}/{path}').content.decode().lower()
                for w in words:
                    self.assertNotIn(w, html, (lang, path, w))
                self.assertNotIn('/prices', html)
                self.assertNotIn('href=""', html)
                self.assertNotIn('details →', html)
                self.assertNotIn('részletek →', html)
                self.assertNotIn('pricerange', html)
        for path in ('/en/prices/', '/hu/prices/', '/api/prices/'):
            self.assertEqual(self.client.get(path).status_code, 404, path)

    def test_static_export_has_no_prices_page(self):
        out = tempfile.mkdtemp()
        call_command('export_static', out=out, api_url='', verbosity=0, site_url='https://example.com/', clean_urls=True)
        p = pathlib.Path(out)
        self.assertFalse((p / 'prices.html').exists() or (p / 'hu' / 'prices.html').exists())
        for f in ('sitemap.xml', 'llms.txt', 'index.html', 'hu/index.html', 'services.html'):
            txt = (p / f).read_text(encoding='utf-8').lower()
            self.assertNotIn('prices', txt, f)
            self.assertNotIn('massage', txt, f)
            self.assertNotIn('masszázs', txt, f)
        self.assertEqual((p / 'sitemap.xml').read_text(encoding='utf-8').count('<url>'), 12)   # (home, treatments, blog + 3 posts) x EN + HU

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
            for path in ['', 'services/', 'blog/']:
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
        self.assertEqual(sm.count('<loc>'), 2 * (3 + BlogPost.objects.filter(is_published=True).count()))
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


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class ApiSourceTests(TestCase):
    """`export_static --from-api` (content read from the JSON API) must render exactly what the database renders."""

    @classmethod
    def setUpTestData(cls):
        call_command('load_initial_content', verbosity=0)
        call_command('load_clinic_media', verbosity=0)

    def _export(self, **kw):
        out = tempfile.mkdtemp()
        call_command('export_static', out=out, api_url='/api/contact/', site_url='https://example.test/', clean_urls=True, verbosity=0, **kw)
        return pathlib.Path(out)

    def test_api_export_equals_database_export(self):
        from unittest import mock
        from .api_source import ApiSource
        import json

        test = self

        class LocalApi(ApiSource):   # same JSON as the live API, served by the Django test client instead of the network
            def _want(self, name):
                pass

            def get(self, path, lang):
                r = test.client.get(path, {'lang': lang})
                assert r.status_code == 200, path
                return json.loads(r.content)

        db = self._export()
        with mock.patch('content.management.commands.export_static.ApiSource', LocalApi):
            api = self._export(from_api='http://testserver')
        files = sorted(p.relative_to(db) for p in db.rglob('*') if p.is_file() and 'assets' not in p.parts)
        self.assertIn(pathlib.Path('hu/blog.html'), files)
        self.assertTrue(any(f.parts[0] == 'blog' for f in files))
        for f in files:
            self.assertEqual((db / f).read_text(encoding='utf-8'), (api / f).read_text(encoding='utf-8'), f)

    def test_unpublished_post_is_not_exported_from_api(self):
        from unittest import mock
        from .api_source import ApiSource
        import json
        test = self

        class LocalApi(ApiSource):
            def _want(self, name):
                pass

            def get(self, path, lang):
                return json.loads(test.client.get(path, {'lang': lang}).content)

        BlogPost.objects.update(is_published=False)
        with mock.patch('content.management.commands.export_static.ApiSource', LocalApi):
            out = self._export(from_api='http://testserver')
        self.assertEqual(list((out / 'blog').glob('*.html')), [])


class LiveContentTests(TestCase):
    """The static pages carry fingerprints (`data-fp`) that js/main.js recomputes from the live API (see README "Live content")."""

    @classmethod
    def setUpTestData(cls):
        call_command('load_initial_content', verbosity=0)
        call_command('load_clinic_media', verbosity=0)

    def _export(self):
        out = tempfile.mkdtemp()
        call_command('export_static', out=out, api_url='https://api.test/api/contact/', site_url='https://example.test/', clean_urls=True, verbosity=0)
        return pathlib.Path(out)

    def test_python_fingerprint(self):
        from . import live
        self.assertEqual(live.fp({'b': [1, 'é'], 'a': '../assets/media/x%20y.webp'}), live.fp({'a': '~/x%20y.webp', 'b': [1, '\u00e9']}))
        self.assertNotEqual(live.fp({'a': 1}), live.fp({'a': 2}))
        self.assertRegex(live.fp({}), r'^[0-9a-f]+-2$')

    def test_markers_in_exported_pages(self):
        out = self._export()
        home = (out / 'index.html').read_text(encoding='utf-8')
        for key in ('hero', 'marquee', 'f1', 'f2', 'counters', 'gallery', 'clips', 'watch', 'cta', 'contact'):
            self.assertRegex(home, rf'data-live="{key}" data-fp="[0-9a-f]+-\d+"', key)
        self.assertRegex((out / 'services.html').read_text(encoding='utf-8'), r'data-live="services" data-fp="[0-9a-f]+-\d+"')
        self.assertRegex((out / 'hu' / 'blog.html').read_text(encoding='utf-8'), r'data-live="blog" data-fp="[0-9a-f]+-\d+"')
        post = next((out / 'blog').glob('what-to-expect*.html')).read_text(encoding='utf-8')
        self.assertRegex(post, r'data-live="post" data-fp="[0-9a-f]+-\d+"')
        self.assertIn('data-slug="what-to-expect-at-your-first-visit"', post)
        self.assertIn('data-s="phone"', home)
        self.assertIn('data-slugs="', home)

    def test_fallback_page_for_new_posts(self):
        out = self._export()
        for folder in (out, out / 'hu'):
            shell = (folder / 'blog' / 'post.html').read_text(encoding='utf-8')
            self.assertIn('<meta name="robots" content="noindex">', shell)
            self.assertIn(' data-shell', shell)
            self.assertIn('data-live="post" data-fp=""', shell)
            self.assertNotIn('Infinite Care1', shell)
        self.assertNotIn('post.html', (out / 'sitemap.xml').read_text(encoding='utf-8'))
        self.assertNotIn('post.html', (out / 'llms.txt').read_text(encoding='utf-8'))

    def test_js_fingerprint_matches_python(self):
        """Runs the real fp() from js/main.js in node over the API responses and compares with the exported data-fp values."""
        import json
        import shutil
        import subprocess
        node = shutil.which('node')
        if not node:
            self.skipTest('node not installed')
        js = (pathlib.Path(__file__).resolve().parents[2] / 'js' / 'main.js').read_text(encoding='utf-8')
        a, z = js.index('const MEDIA='), js.index('// helpers')
        out = self._export()

        def api(path, lang):
            return self.client.get(path, {'lang': lang}).json()

        cases = []   # (file, key, data)
        for lang, folder in (('en', out), ('hu', out / 'hu')):
            h = api('/api/home/', lang)
            g = api('/api/gallery/', lang)
            home = (folder / 'index.html').read_text(encoding='utf-8')
            cases += [(home, 'hero', [h['hero_image'], h['hello'], h['h1_main'], h['h1_em'], h['lead']]), (home, 'marquee', h['marquee']),
                      (home, 'f1', h['f1']), (home, 'f2', h['f2']), (home, 'counters', h['counters']),
                      (home, 'cta', [h['cta_image'], h['cta_script'], h['cta_title'], h['cta_button']]),
                      (home, 'contact', [h['contact_eyebrow'], h['contact_title'], h['contact_text'], h['contact_image']]),
                      (home, 'gallery', {'photos': g['photos'], 'yt': g['youtube'], 'clips': g['videos']}),
                      ((folder / 'services.html').read_text(encoding='utf-8'), 'services', api('/api/services/', lang)['results']),
                      ((folder / 'blog.html').read_text(encoding='utf-8'), 'blog', api('/api/blog/', lang)['results'])]
            post = api('/api/blog/what-to-expect-at-your-first-visit/', lang)
            cases.append(((folder / 'blog' / 'what-to-expect-at-your-first-visit.html').read_text(encoding='utf-8'), 'post', post))
        script = ('const b={dataset:{}};const api="http://testserver";' + js[a:z] +
                  'const c=JSON.parse(require("fs").readFileSync(0,"utf8"));console.log(JSON.stringify(c.map(([k,x])=>fp(k==="blog"||k==="post"?nourl(x):x))))')
        res = subprocess.run([node, '-e', script], input=json.dumps([[c[1], c[2]] for c in cases]), capture_output=True, text=True, check=True)
        for (html, key, _), got in zip(cases, json.loads(res.stdout)):
            m = re.search(rf'data-live="{key}" data-fp="([^"]+)"', html)
            self.assertEqual(m.group(1), got, f"{key}")
