from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'category', 'is_public', 'uploaded_by', 'uploaded_at')
    list_filter = ('category', 'is_public', 'organization')
    search_fields = ('title', 'organization__name')