from django.db import models
from apps.organizations.models import Organization

class StudentAgenda(models.Model):
    title = models.CharField(max_length=200)
    academic_year = models.CharField(max_length=20, help_text="e.g. 2024-2025")
    description = models.TextField()

    def __str__(self):
        return f"{self.title} ({self.academic_year})"


class KPITarget(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='kpi_targets')
    agenda = models.ForeignKey(StudentAgenda, on_delete=models.CASCADE, related_name='kpi_targets')
    metric_name = models.CharField(max_length=150, help_text="e.g. Attendees Reached, Workshops Hosted")
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    achieved_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def progress_percentage(self):
        if self.target_value and self.target_value > 0:
            pct = int((self.achieved_value / self.target_value) * 100)
            return min(pct, 100)
        return 0

    def __str__(self):
        return f"{self.organization.acronym or self.organization.name} - {self.metric_name}"