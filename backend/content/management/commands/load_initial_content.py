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

from content import service_pages
from content.models import (SiteSettings, HomePage, Counter, Service,
                            GalleryItem, VideoClip, YouTubeVideo, BlogPost)

SEED = Path(__file__).resolve().parents[2] / 'seed' / 'initial_content.json'
IMAGES = settings.SITE_ROOT / 'assets' / 'images'   # seed images (may be in a sub-folder, e.g. gallery/x.webp)
VIDEOS = settings.SITE_ROOT / 'assets' / 'video'


def attach(obj, field, filename, folder, base=IMAGES):
    if not filename:
        return
    name = Path(filename).name
    if not getattr(settings, 'CONTENT_SEED_FILES', True):
        # e.g. on Cloudflare Workers: reference the image already shipped as a static asset (assets/media/<folder>/<file>)
        getattr(obj, field).name = f'{folder}/{name}'
        return
    with (base / filename).open('rb') as fh:
        getattr(obj, field).save(name, File(fh), save=False)


def load_blog(d):
    """Create the starter blog posts (DRAFT COPY for the clinic to review) from the seed data."""
    import datetime
    for b in d.get('blog', []):
        if BlogPost.objects.filter(slug=b['slug']).exists():
            continue
        obj = BlogPost(**{k: v for k, v in b.items() if k not in ('image', 'published_at')},
                       published_at=datetime.date.fromisoformat(b['published_at']))
        attach(obj, 'cover', b['image'], 'blog')
        obj.save()
    return BlogPost.objects.count()


def load_gallery(d):
    """Create the gallery photos and video clips from the seed data (files are copied into MEDIA_ROOT)."""
    for i, g in enumerate(d.get('gallery', [])):
        obj = GalleryItem(order=(i + 1) * 10, **{k: v for k, v in g.items() if k != 'image'})
        attach(obj, 'image', g['image'], 'gallery')
        obj.save()
    for i, c in enumerate(d.get('clips', [])):
        obj = VideoClip(order=(i + 1) * 10, category=c.get('category', 'treatments'), title_en=c['title_en'], title_hu=c['title_hu'])
        attach(obj, 'video', c['video'], 'video', VIDEOS)
        attach(obj, 'poster', c['poster'], 'video', VIDEOS)
        obj.save()
    return GalleryItem.objects.count(), VideoClip.objects.count()


def load_youtube(d):
    """Create the YouTube videos from the seed data (only those whose ID is not in the database yet). Returns how many were created."""
    n = 0
    for i, v in enumerate(d.get('youtube', [])):
        if YouTubeVideo.objects.filter(youtube_id=v['youtube_id'], language=v['language']).exists():
            continue
        f = {k: x for k, x in v.items() if k not in ('poster', 'service', 'post')}
        obj = YouTubeVideo(order=(i + 1) * 10, **f)
        obj.service = Service.objects.filter(title_en=v['service']).first() if v.get('service') else None
        obj.post = BlogPost.objects.filter(slug=v['post']).first() if v.get('post') else None
        attach(obj, 'poster', v['poster'], 'youtube')
        obj.save()
        n += 1
    return n


class Command(BaseCommand):
    help = 'Load the original site content (texts, images) into the database'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Delete existing content first')

    @transaction.atomic
    def handle(self, *args, force=False, **kw):
        if Service.objects.exists() and not force:
            self.stdout.write('Content already present – nothing to do (use --force to reload).')
            return
        for m in (BlogPost, GalleryItem, VideoClip, YouTubeVideo, Service, Counter, HomePage, SiteSettings):
            m.objects.all().delete() if m not in (HomePage, SiteSettings) else m.objects.filter().delete()
        for folder in ('home', 'services', 'gallery', 'video', 'youtube', 'blog') if getattr(settings, 'CONTENT_SEED_FILES', True) else ():
            shutil.rmtree(Path(settings.MEDIA_ROOT) / folder, ignore_errors=True)
        if SEED.exists():
            d = json.loads(SEED.read_text(encoding='utf-8'))
        else:  # bundles that ship only .py files (Cloudflare Python Workers)
            from content.seed.seed_data import DATA as d

        SiteSettings(**d['settings']).save()
        home = dict(d['home'])
        images = {k: home.pop(k) for k in ('hero_image', 'f1_image', 'f2_image', 'cta_image', 'contact_image')}
        h = HomePage(**home)
        for k, fn in images.items():
            attach(h, k, fn, 'home')
        h.save()
        for i, c in enumerate(d['counters']):
            Counter.objects.create(order=i, **c)
        for i, s in enumerate(d['services']):
            s = dict(s)
            obj = Service(order=(i + 1) * 10, **{k: v for k, v in s.items() if k != 'image'})
            attach(obj, 'image', s['image'], 'services')
            obj.save()
        service_pages.fill(Service)   # text / URLs of the service landing pages
        photos, clips = load_gallery(d)
        posts = load_blog(d)
        load_youtube(d)
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {Service.objects.count()} services, "
            f"{Counter.objects.count()} counters, {photos} gallery photos, {clips} video clips, {posts} blog posts, site settings and home page."))
