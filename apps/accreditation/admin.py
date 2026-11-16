from django.contrib import admin
from .models import (
    AccreditationCycle,
    AccreditationRequirement,
    AccreditationSubmission,
    SubmittedDocument,
)

@admin.register(AccreditationCycle)
class AccreditationCycleAdmin(admin.ModelAdmin):
    list_display = ('title', 'academic_year', 'start_date', 'is_active')
    list_filter = ('is_active', 'academic_year')
    search_fields = ('title', 'academic_year')

@admin.register(AccreditationRequirement)
class AccreditationRequirementAdmin(admin.ModelAdmin):
    list_display = ('title', 'cycle', 'is_mandatory')
    list_filter = ('cycle', 'is_mandatory')
    search_fields = ('title',)

@admin.register(AccreditationSubmission)
class AccreditationSubmissionAdmin(admin.ModelAdmin):
    list_display = ('organization', 'cycle', 'status', 'submitted_by', 'reviewed_by')
    list_filter = ('status', 'cycle')
    search_fields = ('organization__name', 'submitted_by__username')

@admin.register(SubmittedDocument)
class SubmittedDocumentAdmin(admin.ModelAdmin):
    list_display = ('submission', 'requirement', 'document')