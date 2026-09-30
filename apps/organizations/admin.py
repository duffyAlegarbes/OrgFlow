from django.contrib import admin
from .models import Organization, OrganizationMembership

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'category', 'status', 'created_by', 'created_at')
    list_filter = ('category', 'status')
    search_fields = ('name', 'acronym', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'status', 'created_at')
    list_filter = ('role', 'status', 'organization')
    search_fields = ('user__username', 'organization__name')