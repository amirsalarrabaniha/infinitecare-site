"""Seed the database with the original Infinite Care content (EN + HU) and copy images into MEDIA_ROOT.

    python manage.py load_initial_content          # only if the DB has no content yet
    python manage.py load_initial_content --force  # wipe content tables and reload
"""
import json
import shutil
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import SiteSettings, HomePage, Counter, Service, Package, PriceCategory, PriceItem

SEED = Path(__file__).resolve().parents[2] / 'seed' / 'initial_content.json'
IMAGES = settings.SITE_ROOT / 'assets' / 'images'


def attach(obj, field, filename, folder):
    if not filename:
        return
    if not getattr(settings, 'CONTENT_SEED_FILES', True):
        # e.g. on Cloudflare Workers: reference the image already shipped as a static asset (assets/media/<folder>/<file>)
        getattr(obj, field).name = f'{folder}/{filename}'
        return
    src = IMAGES / filename
    with src.open('rb') as fh:
        getattr(obj, field).save(filename, File(fh), save=False)


class Command(BaseCommand):
    help = 'Load the original site content (texts, prices, images) into the database'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Delete existing content first')

    @transaction.atomic
    def handle(self, *args, force=False, **kw):
        if Service.objects.exists() and not force:
            self.stdout.write('Content already present – nothing to do (use --force to reload).')
            return
        for m in (PriceItem, PriceCategory, Package, Service, Counter, HomePage, SiteSettings):
            m.objects.all().delete() if m not in (HomePage, SiteSettings) else m.objects.filter().delete()
        for folder in ('home', 'services', 'packages') if getattr(settings, 'CONTENT_SEED_FILES', True) else ():
            shutil.rmtree(Path(settings.MEDIA_ROOT) / folder, ignore_errors=True)
        if SEED.exists():
            d = json.loads(SEED.read_text(encoding='utf-8'))
        else:  # bundles that ship only .py files (Cloudflare Python Workers)
            from content.seed.seed_data import DATA as d

        SiteSettings(**d['settings']).save()
        home = dict(d['home'])
        images = {k: home.pop(k) for k in ('hero_image', 'f1_image', 'f2_image', 'cta_image')}
        h = HomePage(**home)
        for k, fn in images.items():
            attach(h, k, fn, 'home')
        h.save()
        for i, c in enumerate(d['counters']):
            Counter.objects.create(order=i, **c)
        for i, s in enumerate(d['services']):
            s = dict(s)
            obj = Service(order=(i + 1) * 10, **{k: v for k, v in s.items() if k != 'image'})
            obj.show_details = s['title_en'] != 'Esthetic treatments'
            attach(obj, 'image', s['image'], 'services')
            obj.save()
        for i, p in enumerate(d['packages']):
            Package.objects.create(order=(i + 1) * 10, **{k: v for k, v in p.items() if k != 'image'})
        for i, c in enumerate(d['price_categories']):
            cat = PriceCategory.objects.create(order=(i + 1) * 10, title_en=c['title_en'], title_hu=c['title_hu'])
            PriceItem.objects.bulk_create(PriceItem(category=cat, order=j, **it) for j, it in enumerate(c['items']))
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {Service.objects.count()} services, {Package.objects.count()} packages, "
            f"{PriceCategory.objects.count()} price categories / {PriceItem.objects.count()} items, "
            f"{Counter.objects.count()} counters, site settings and home page."))
