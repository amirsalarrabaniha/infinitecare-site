from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, HomePage, Counter, Service, Package, PriceCategory, PriceItem

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
        ('Social & map', {'fields': ['facebook', 'instagram', 'youtube', 'map_embed']}),
    ]


@admin.register(HomePage)
class HomePageAdmin(SingletonAdmin):
    fieldsets = [
        ('Hero', {'fields': ['hero_image', *pairs('hello', 'h1', 'lead', 'marquee')]}),
        ('Section 1', {'fields': ['f1_image', *pairs('f1_eyebrow', 'f1_title', 'f1_text', 'f1_button')]}),
        ('Section 2', {'fields': ['f2_image', *pairs('f2_eyebrow', 'f2_title', 'f2_text', 'f2_button')]}),
        ('Consultation banner', {'fields': ['cta_image', *pairs('cta_s', 'cta', 'cta_b')]}),
        ('Contact section', {'fields': pairs('contact', 'c_h', 'c_p')}),
    ]


class Thumb:
    @admin.display(description='Image')
    def thumb(self, obj):
        return format_html('<img src="{}" style="height:48px;border-radius:6px">', obj.image.url) if obj.image else '–'


@admin.register(Service)
class ServiceAdmin(Thumb, admin.ModelAdmin):
    list_display = ['thumb', 'title_en', 'title_hu', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_display_links = ['thumb', 'title_en']
    search_fields = ['title_en', 'title_hu']
    fields = ['image', ('order', 'is_active', 'show_details'), *pairs('eyebrow', 'title', 'description')]


@admin.register(Package)
class PackageAdmin(Thumb, admin.ModelAdmin):
    list_display = ['name_en', 'name_hu', 'price', 'order', 'is_active']
    list_editable = ['price', 'order', 'is_active']
    fields = [('order', 'is_active'), *pairs('name', 'items'), 'price', 'image']


@admin.register(Counter)
class CounterAdmin(admin.ModelAdmin):
    list_display = ['value', 'suffix', 'label_en', 'label_hu', 'order', 'is_active']
    list_editable = ['suffix', 'label_en', 'label_hu', 'order', 'is_active']
    list_display_links = ['value']


class PriceItemInline(admin.TabularInline):
    model = PriceItem
    extra = 1
    fields = ['order', 'label_en', 'label_hu', 'price_en', 'price_hu', 'is_subheading']


@admin.register(PriceCategory)
class PriceCategoryAdmin(admin.ModelAdmin):
    list_display = ['title_en', 'title_hu', 'item_count', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    inlines = [PriceItemInline]
    fields = [('order', 'is_active'), ('title_en', 'title_hu')]

    @admin.display(description='Items')
    def item_count(self, obj):
        return obj.items.count()
