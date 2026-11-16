from django.contrib import admin
from .models import Post, PartnershipRequest

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'post_type', 'author', 'created_at')
    list_filter = ('post_type', 'organization')
    search_fields = ('title', 'content', 'organization__name')

@admin.register(PartnershipRequest)
class PartnershipRequestAdmin(admin.ModelAdmin):
    list_display = ('post', 'target_category', 'status')
    list_filter = ('status', 'target_category')