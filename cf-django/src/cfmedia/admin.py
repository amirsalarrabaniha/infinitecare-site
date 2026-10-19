from django.contrib import admin
from .models import StoredFile


@admin.register(StoredFile)
class StoredFileAdmin(admin.ModelAdmin):
    list_display = ["name", "content_type", "size", "created_at"]
    exclude = ["content"]
