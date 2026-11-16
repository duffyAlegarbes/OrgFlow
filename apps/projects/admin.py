from django.contrib import admin
from .models import Project, ProjectActivity

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'status', 'budget_allocated', 'date_start')
    list_filter = ('status', 'organization')
    search_fields = ('title', 'organization__name')

@admin.register(ProjectActivity)
class ProjectActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status')
    list_filter = ('status', 'project__organization')