from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'name', 'email', 'phone', 'language', 'short_message', 'is_read']
    list_filter = ['is_read', 'language', 'created_at']
    list_editable = ['is_read']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['name', 'email', 'phone', 'message', 'language', 'created_at', 'ip_address']
    actions = ['mark_read', 'mark_unread']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    @admin.display(description='Message')
    def short_message(self, obj):
        return obj.message[:80] + ('…' if len(obj.message) > 80 else '')

    @admin.action(description='Mark selected as read')
    def mark_read(self, request, qs):
        self.message_user(request, f'{qs.update(is_read=True)} message(s) marked read.')

    @admin.action(description='Mark selected as unread')
    def mark_unread(self, request, qs):
        self.message_user(request, f'{qs.update(is_read=False)} message(s) marked unread.')

    def changeform_view(self, request, object_id=None, *a, **kw):
        if object_id:
            ContactMessage.objects.filter(pk=object_id, is_read=False).update(is_read=True)
        return super().changeform_view(request, object_id, *a, **kw)
