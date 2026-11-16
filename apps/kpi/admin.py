from django.contrib import admin
from .models import StudentAgenda, KPITarget

@admin.register(StudentAgenda)
class StudentAgendaAdmin(admin.ModelAdmin):
    list_display = ('title', 'academic_year')
    list_filter = ('academic_year',)
    search_fields = ('title', 'description')

@admin.register(KPITarget)
class KPITargetAdmin(admin.ModelAdmin):
    list_display = ('metric_name', 'organization', 'agenda', 'target_value', 'achieved_value')
    list_filter = ('organization', 'agenda')
    search_fields = ('metric_name', 'organization__name')