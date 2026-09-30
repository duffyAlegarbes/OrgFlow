from django.db import models
from apps.organizations.models import Organization

class StudentAgenda(models.Model):
    title = models.CharField(max_length=200)
    academic_year = models.CharField(max_length=20)
    description = models.TextField()

    def __str__(self):
        return f"{self.title} ({self.academic_year})"

class KPITarget(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='kpi_targets')
    agenda = models.ForeignKey(StudentAgenda, on_delete=models.CASCADE, related_name='kpi_targets')
    metric_name = models.CharField(max_length=150)
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    achieved_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.organization.acronym or self.organization.name} - {self.metric_name}"