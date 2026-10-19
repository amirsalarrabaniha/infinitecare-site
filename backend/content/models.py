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
    show_details = models.BooleanField('Show "Details" link', default=True)

    class Meta(Ordered.Meta):
        pass

    def __str__(self):
        return self.title_en


class Package(Ordered):
    name_en = models.CharField(max_length=80)
    name_hu = models.CharField(max_length=80, blank=True)
    items_en = models.TextField('Description / items (EN)', help_text='One item per line')
    items_hu = models.TextField('Description / items (HU)', blank=True)
    price = models.CharField(max_length=40, help_text='e.g. 309 000')
    image = models.ImageField(upload_to='packages/', blank=True)

    class Meta(Ordered.Meta):
        pass

    def __str__(self):
        return self.name_en


class PriceCategory(Ordered):
    title_en = models.CharField(max_length=150)
    title_hu = models.CharField(max_length=150, blank=True)

    class Meta(Ordered.Meta):
        verbose_name_plural = 'Price categories'

    def __str__(self):
        return self.title_en


class PriceItem(Bilingual):
    category = models.ForeignKey(PriceCategory, related_name='items', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    label_en = models.CharField(max_length=250)
    label_hu = models.CharField(max_length=250, blank=True)
    price_en = models.CharField(max_length=40, blank=True, help_text='e.g. 70.000 HUF (empty for sub-headings)')
    price_hu = models.CharField(max_length=40, blank=True, help_text='e.g. 70.000 Ft')
    is_subheading = models.BooleanField(default=False)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.label_en
