from django.contrib import admin
from django.utils.html import format_html, format_html_join
from .models import SiteSettings, HomePage, Counter, Service, GalleryItem, VideoClip, YouTubeVideo, BlogPost

admin.site.site_header = 'Infinite Care admin'
admin.site.site_title = 'Infinite Care'
admin.site.index_title = 'Website content & messages'


def pairs(*names):
    return [(f'{n}_en', f'{n}_hu') for n in names]


class SingletonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = [
        ('Contact', {'fields': ['phone', 'email', *pairs('address'), 'city']}),
        ('Opening hours & footer', {'fields': pairs('hours', 'tagline')}),
        ('Social & map', {'fields': ['facebook', 'instagram', 'youtube', 'tiktok', 'map_embed']}),
        ('Online booking', {'fields': ['booking_url', 'offers_url']}),
    ]


@admin.register(HomePage)
class HomePageAdmin(SingletonAdmin):
    fieldsets = [
        ('Hero', {'fields': ['hero_image', *pairs('hello', 'h1', 'lead', 'marquee')]}),
        ('Section 1', {'fields': ['f1_image', *pairs('f1_eyebrow', 'f1_title', 'f1_text', 'f1_button')]}),
        ('Section 2', {'fields': ['f2_image', *pairs('f2_eyebrow', 'f2_title', 'f2_text', 'f2_button')]}),
        ('Consultation banner', {'fields': ['cta_image', *pairs('cta_s', 'cta', 'cta_b')]}),
        ('Contact section', {'fields': ['contact_image', *pairs('contact', 'c_h', 'c_p')]}),
    ]


class Thumb:
    @admin.display(description='Image')
    def thumb(self, obj):
        return format_html('<img src="{}" style="height:48px;border-radius:6px">', obj.image.url) if obj.image else '–'


@admin.register(Service)
class ServiceAdmin(Thumb, admin.ModelAdmin):
    list_editable = ['order', 'is_active']
    list_display_links = ['thumb', 'title_en']
    search_fields = ['title_en', 'title_hu']
    list_display = ['thumb', 'title_en', 'title_hu', 'page_links', 'order', 'is_active']
    fieldsets = [
        (None, {'fields': ['image', ('order', 'is_active'), *pairs('eyebrow', 'title', 'description')]}),
        ('Service page (own URL for Google)', {
            'description': 'Each service can have its own page on the website, e.g. /carbon-peeling (EN) and /carbon-hamlasztas (HU). '
                           'The page shows the text below, the YouTube videos linked to this service and the gallery photos of the chosen category. '
                           'Changes show on the live pages; new URLs need a site export (see README).',
            'fields': [('slug_en', 'slug_hu'), *pairs('meta_title', 'meta_description', 'body'), 'gallery_category']}),
    ]

    @admin.display(description='Page')
    def page_links(self, obj):
        slugs = [(s,) for s in (obj.slug_en, obj.slug_hu) if s]
        return format_html_join(' · ', '<code>/{}</code>', slugs) if slugs else '–'


@admin.register(Counter)
class CounterAdmin(admin.ModelAdmin):
    list_display = ['value', 'suffix', 'label_en', 'label_hu', 'order', 'is_active']
    list_editable = ['suffix', 'label_en', 'label_hu', 'order', 'is_active']
    list_display_links = ['value']


@admin.register(GalleryItem)
class GalleryItemAdmin(Thumb, admin.ModelAdmin):
    list_display = ['thumb', 'alt_en', 'alt_hu', 'category', 'order', 'is_active']
    list_editable = ['category', 'order', 'is_active']
    list_display_links = ['thumb', 'alt_en']
    list_filter = ['category']
    fields = ['image', ('category', 'order', 'is_active'), *pairs('alt')]


@admin.register(VideoClip)
class VideoClipAdmin(admin.ModelAdmin):
    list_display = ['title_en', 'title_hu', 'category', 'order', 'is_active']
    list_editable = ['category', 'order', 'is_active']
    list_filter = ['category']
    fields = [('order', 'is_active', 'category'), 'video', 'poster', *pairs('title')]


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ['title_en', 'youtube_id', 'category', 'language', 'featured', 'show_on_home', 'show_in_gallery', 'service', 'post', 'order', 'is_active']
    list_editable = ['category', 'language', 'featured', 'show_on_home', 'show_in_gallery', 'order', 'is_active']
    list_filter = ['category', 'language', 'is_active']
    search_fields = ['title_en', 'title_hu', 'youtube_id']
    fieldsets = [
        ('Video', {'fields': ['youtube_id', 'poster', ('vertical', 'language'), ('order', 'is_active')]}),
        ('Text', {'fields': [*pairs('title', 'caption')]}),
        ('Where it appears', {'fields': ['category', ('featured', 'show_on_home', 'show_in_gallery'), 'service', 'post']}),
    ]


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['thumb', 'title_en', 'title_hu', 'published_at', 'is_published']
    list_editable = ['is_published']
    list_display_links = ['thumb', 'title_en']
    list_filter = ['is_published']
    search_fields = ['title_en', 'title_hu', 'slug']
    prepopulated_fields = {'slug': ('title_en',)}
    fieldsets = [
        (None, {'fields': ['title_en', 'title_hu', 'slug', ('published_at', 'is_published'), 'cover']}),
        ('English', {'fields': ['excerpt_en', 'body_en']}),
        ('Magyar', {'fields': ['excerpt_hu', 'body_hu']}),
    ]

    @admin.display(description='Cover')
    def thumb(self, obj):
        return format_html('<img src="{}" style="height:48px;border-radius:6px">', obj.cover.url) if obj.cover else '–'
