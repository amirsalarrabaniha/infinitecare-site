"""Add the clinic photo gallery / video clips, the starter blog posts and the real clinic photos to a database that was seeded earlier.

    python manage.py load_clinic_media                # create gallery + clips if there are none yet
    python manage.py load_clinic_media --update-images  # also swap the hero / section / contact / service images

(A fresh database gets all of this from `load_initial_content`.)
"""
import json

from django.core.management.base import BaseCommand
from django.db import transaction

from content.management.commands.load_initial_content import SEED, attach, load_blog, load_gallery
from content.models import GalleryItem, HomePage, Service, VideoClip


class Command(BaseCommand):
    help = 'Add the gallery photos, video clips and clinic photos from the seed file to an existing database'

    def add_arguments(self, parser):
        parser.add_argument('--update-images', action='store_true',
                            help='Replace the home page (hero, sections, contact) and service images with the seed images')

    @transaction.atomic
    def handle(self, *args, update_images=False, **kw):
        if SEED.exists():
            d = json.loads(SEED.read_text(encoding='utf-8'))
        else:
            from content.seed.seed_data import DATA as d
        if GalleryItem.objects.exists() or VideoClip.objects.exists():
            self.stdout.write('Gallery already present - not touching it.')
        else:
            photos, clips = load_gallery(d)
            self.stdout.write(self.style.SUCCESS(f'Created {photos} gallery photos and {clips} video clips.'))
        n = load_blog(d)
        self.stdout.write(f'Blog posts in the database: {n} (starter posts are only added when their slug is missing).')
        if update_images:
            h = HomePage.load()
            for k in ('hero_image', 'f1_image', 'f2_image', 'contact_image'):
                attach(h, k, d['home'][k], 'home')
            h.save()
            for s in d['services']:
                if s['image'].startswith('gallery/'):
                    obj = Service.objects.filter(title_en=s['title_en']).first()
                    if obj:
                        attach(obj, 'image', s['image'], 'services')
                        obj.save()
            self.stdout.write(self.style.SUCCESS('Home page and service images updated.'))
