import datetime

from django.core.validators import RegexValidator
from django.db import models

LANGS = ('en', 'hu')


class Bilingual(models.Model):
    """Helper: obj.tr('title', 'hu') returns title_hu, falling back to English."""
    class Meta:
        abstract = True

    def tr(self, field, lang):
        return getattr(self, f'{field}_{lang}', '') or getattr(self, f'{field}_en', '')

    def localized(self, lang, fields):
        return {f: self.tr(f, lang) for f in fields}


class Singleton(Bilingual):
    class Meta:
        abstract = True

    def save(self, *a, **kw):
        self.pk = 1
        super().save(*a, **kw)

    def delete(self, *a, **kw):
        pass

    @classmethod
    def load(cls):
        return cls.objects.get_or_create(pk=1)[0]


class SiteSettings(Singleton):
    phone = models.CharField(max_length=40, default='+36 1 707 0075')
    email = models.EmailField(default='info@infinitecare.hu')
    address_en = models.CharField('Address (EN)', max_length=200, blank=True)
    address_hu = models.CharField('Address (HU)', max_length=200, blank=True)
    hours_en = models.TextField('Opening hours (EN)', blank=True, help_text='One line per row')
    hours_hu = models.TextField('Opening hours (HU)', blank=True)
    tagline_en = models.CharField('Footer tagline (EN)', max_length=200, blank=True)
    tagline_hu = models.CharField('Footer tagline (HU)', max_length=200, blank=True)
    city = models.CharField(max_length=100, default='Budapest, Hungary')
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    offers_url = models.URLField('"Offers" menu link', max_length=500, default='https://l.fresha.com/3yv8307j6', blank=True,
                                 help_text='External page opened in a new tab from the "Offers" item in the header menu. Leave empty to hide the item.')
    booking_url = models.URLField('Online booking link (Fresha)', max_length=500, default='https://l.fresha.com/3dvz3n7j6',
                                  help_text='Opens in a new tab from the "Book now" buttons. Leave empty to hide all online-booking buttons and sections.')
    map_embed = models.URLField('Google Maps embed URL', max_length=1000, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = 'Site settings'

    def __str__(self):
        return 'Site settings'

    @property
    def phone_href(self):
        return 'tel:' + ''.join(c for c in self.phone if c.isdigit() or c == '+')


class HomePage(Singleton):
    hero_image = models.ImageField(upload_to='home/', blank=True)
    hello_en = models.CharField('Hero script (EN)', max_length=100, blank=True)
    hello_hu = models.CharField('Hero script (HU)', max_length=100, blank=True)
    h1_en = models.CharField('Hero title (EN)', max_length=200, blank=True, help_text='Use | to split into the highlighted second line')
    h1_hu = models.CharField('Hero title (HU)', max_length=200, blank=True)
    lead_en = models.TextField('Hero text (EN)', blank=True)
    lead_hu = models.TextField('Hero text (HU)', blank=True)
    marquee_en = models.TextField('Scrolling strip (EN)', blank=True, help_text='Comma separated')
    marquee_hu = models.TextField('Scrolling strip (HU)', blank=True)
    f1_image = models.ImageField('Section 1 image', upload_to='home/', blank=True)
    f1_eyebrow_en = models.CharField(max_length=100, blank=True)
    f1_eyebrow_hu = models.CharField(max_length=100, blank=True)
    f1_title_en = models.CharField(max_length=200, blank=True)
    f1_title_hu = models.CharField(max_length=200, blank=True)
    f1_text_en = models.TextField(blank=True, help_text='Blank line = new paragraph')
    f1_text_hu = models.TextField(blank=True)
    f1_button_en = models.CharField(max_length=100, blank=True)
    f1_button_hu = models.CharField(max_length=100, blank=True)
    f2_image = models.ImageField('Section 2 image', upload_to='home/', blank=True)
    f2_eyebrow_en = models.CharField(max_length=100, blank=True)
    f2_eyebrow_hu = models.CharField(max_length=100, blank=True)
    f2_title_en = models.CharField(max_length=200, blank=True)
    f2_title_hu = models.CharField(max_length=200, blank=True)
    f2_text_en = models.TextField(blank=True)
    f2_text_hu = models.TextField(blank=True)
    f2_button_en = models.CharField(max_length=100, blank=True)
    f2_button_hu = models.CharField(max_length=100, blank=True)
    cta_image = models.ImageField('Consultation banner image', upload_to='home/', blank=True)
    cta_s_en = models.CharField('Banner script (EN)', max_length=100, blank=True)
    cta_s_hu = models.CharField('Banner script (HU)', max_length=100, blank=True)
    cta_en = models.CharField('Banner title (EN)', max_length=200, blank=True)
    cta_hu = models.CharField('Banner title (HU)', max_length=200, blank=True)
    cta_b_en = models.CharField('Banner button (EN)', max_length=100, blank=True)
    cta_b_hu = models.CharField('Banner button (HU)', max_length=100, blank=True)
    contact_image = models.ImageField('Contact section photo (clinic entrance)', upload_to='home/', blank=True)
    contact_en = models.CharField('Contact eyebrow (EN)', max_length=100, blank=True)
    contact_hu = models.CharField('Contact eyebrow (HU)', max_length=100, blank=True)
    c_h_en = models.CharField('Contact title (EN)', max_length=200, blank=True)
    c_h_hu = models.CharField('Contact title (HU)', max_length=200, blank=True)
    c_p_en = models.TextField('Contact text (EN)', blank=True)
    c_p_hu = models.TextField('Contact text (HU)', blank=True)

    class Meta:
        verbose_name = verbose_name_plural = 'Home page'

    def __str__(self):
        return 'Home page'


class Ordered(Bilingual):
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['order', 'id']


class Counter(Ordered):
    value = models.PositiveIntegerField()
    suffix = models.CharField(max_length=5, blank=True, default='+')
    label_en = models.CharField(max_length=60)
    label_hu = models.CharField(max_length=60, blank=True)

    class Meta(Ordered.Meta):
        pass

    def __str__(self):
        return f'{self.value} {self.label_en}'


class Service(Ordered):
    image = models.ImageField(upload_to='services/')
    eyebrow_en = models.CharField('Subtitle (EN)', max_length=150, blank=True)
    eyebrow_hu = models.CharField('Subtitle (HU)', max_length=150, blank=True)
    title_en = models.CharField(max_length=150)
    title_hu = models.CharField(max_length=150, blank=True)
    description_en = models.TextField()
    description_hu = models.TextField(blank=True)

    class Meta(Ordered.Meta):
        pass

    def __str__(self):
        return self.title_en


GALLERY_CATEGORIES = [('clinic', 'Clinic'), ('treatments', 'Treatments'), ('events', 'Events'),
                      ('whitening', 'Teeth Whitening'), ('facial', 'Facial'), ('laser', 'Laser'),
                      ('emsculpt', 'Emsculpt'), ('carbon', 'Carbon Peeling'), ('cellulite', 'Cellulite'), ('brazilift', 'Brazilift')]
# specific treatment categories (one per service that has gallery content); their items also show under "Treatments"
TREATMENT_TYPES = ('whitening', 'facial', 'laser', 'emsculpt', 'carbon', 'cellulite', 'brazilift')


class GalleryItem(Ordered):
    """Photo shown in the "Our clinic" gallery on the home page (grid + lightbox)."""
    CATEGORIES = GALLERY_CATEGORIES
    image = models.ImageField(upload_to='gallery/', help_text='Landscape or portrait photo, ideally max 1600 px on the long edge (WebP/JPG)')
    category = models.CharField(max_length=20, choices=CATEGORIES, default='clinic',
                                help_text='Treatment categories (Teeth Whitening, Facial, Laser, Emsculpt, ...) also appear under "Treatments"')
    alt_en = models.CharField('Caption / alt text (EN)', max_length=200)
    alt_hu = models.CharField('Caption / alt text (HU)', max_length=200, blank=True)
    width = models.PositiveIntegerField(default=0, editable=False)
    height = models.PositiveIntegerField(default=0, editable=False)

    class Meta(Ordered.Meta):
        verbose_name = 'Gallery photo'

    def __str__(self):
        return self.alt_en

    def save(self, *a, **kw):
        if self.image and not (self.width and self.height):
            try:  # needs Pillow; seeded items carry their size, so this is only for admin uploads
                self.width, self.height = self.image.width, self.image.height
            except Exception:
                pass
        super().save(*a, **kw)


class VideoClip(Ordered):
    """Short muted looping clip (vertical MP4, H.264, no audio, ideally < 3 MB) shown in the home page video section."""
    video = models.FileField(upload_to='video/', help_text='MP4 (H.264), portrait 720x1280, no audio, under ~3 MB')
    poster = models.ImageField(upload_to='video/', help_text='Still frame shown before the video plays')
    category = models.CharField(max_length=20, choices=GALLERY_CATEGORIES, default='treatments')
    title_en = models.CharField('Caption (EN)', max_length=150)
    title_hu = models.CharField('Caption (HU)', max_length=150, blank=True)

    class Meta(Ordered.Meta):
        verbose_name = 'Video clip'

    def __str__(self):
        return self.title_en


class BlogPost(Bilingual):
    """Blog article (EN + HU). Body: blank line = new paragraph, "## " = sub-heading, lines starting with "- " = bullet list."""
    slug = models.SlugField(unique=True, help_text='Used in the URL: /en/blog/<slug>/ and /hu/blog/<slug>/ (same for both languages)')
    title_en = models.CharField('Title (EN)', max_length=200)
    title_hu = models.CharField('Title (HU)', max_length=200, blank=True)
    excerpt_en = models.TextField('Short summary (EN)', max_length=400, help_text='Shown on the blog list and used as meta description')
    excerpt_hu = models.TextField('Short summary (HU)', max_length=400, blank=True)
    body_en = models.TextField('Article (EN)', help_text='Blank line = new paragraph; "## Heading"; lines starting with "- " make a list')
    body_hu = models.TextField('Article (HU)', blank=True)
    cover = models.ImageField('Cover image', upload_to='blog/', help_text='Landscape photo, ideally 1200-1600 px wide')
    published_at = models.DateField(default=datetime.date.today)
    is_published = models.BooleanField('Published', default=True)

    class Meta:
        ordering = ['-published_at', '-id']
        verbose_name = 'Blog post'

    def __str__(self):
        return self.title_en


class YouTubeVideo(Ordered):
    """A video from the clinic's YouTube channel. Nothing is loaded from YouTube until a visitor clicks play: the page shows
    the poster below (hosted on this site) and only then adds the youtube-nocookie.com player."""
    LANGUAGES = [('', 'Both languages'), ('en', 'English site only'), ('hu', 'Hungarian site only')]
    youtube_id = models.CharField('YouTube video ID', max_length=11, validators=[RegexValidator(r'^[A-Za-z0-9_-]{11}$', 'The 11-character ID from the video address.')],
                                  help_text='The 11 characters after v= in youtube.com/watch?v=..., or at the end of a youtu.be / Shorts link')
    title_en = models.CharField('Title (EN)', max_length=150)
    title_hu = models.CharField('Title (HU)', max_length=150, blank=True)
    caption_en = models.CharField('Short note (EN)', max_length=200, blank=True, help_text='Optional line under the video')
    caption_hu = models.CharField('Short note (HU)', max_length=200, blank=True)
    poster = models.ImageField(upload_to='youtube/', width_field='poster_width', height_field='poster_height',
                               help_text='Still image shown before the video is played (WebP/JPG). 16:9 for normal videos, 9:16 for Shorts')
    poster_width = models.PositiveIntegerField(default=0, editable=False)
    poster_height = models.PositiveIntegerField(default=0, editable=False)
    vertical = models.BooleanField('Vertical (Short)', default=False, help_text='Tick for 9:16 videos / YouTube Shorts')
    language = models.CharField('Show on', max_length=2, blank=True, choices=LANGUAGES, default='',
                                help_text='Use this when there is a separate English and Hungarian version of the same video')
    category = models.CharField('Gallery category', max_length=20, choices=GALLERY_CATEGORIES, default='treatments')
    featured = models.BooleanField('Featured on home page', default=False, help_text='Large video at the top of the home page "Watch us" section')
    show_on_home = models.BooleanField('Home page "Watch us" row', default=False)
    show_in_gallery = models.BooleanField('Show in the gallery', default=True, help_text='Appears under its category tab (and under "Treatments" for treatment categories)')
    service = models.ForeignKey(Service, null=True, blank=True, on_delete=models.SET_NULL, related_name='videos',
                                help_text='Optional: show this video next to this service on the Services page')
    post = models.ForeignKey(BlogPost, null=True, blank=True, on_delete=models.SET_NULL, related_name='videos',
                             help_text='Optional: show this video inside this blog post')

    class Meta(Ordered.Meta):
        verbose_name = 'YouTube video'

    def __str__(self):
        return self.title_en
