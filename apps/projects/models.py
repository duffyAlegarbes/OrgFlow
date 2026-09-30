from django.db import models
from django.contrib.auth.models import User
from apps.organizations.models import Organization

class Project(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Planning', 'In Planning'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Archived', 'Archived'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    budget_allocated = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.organization.name}"

class ProjectActivity(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Done', 'Done'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=150)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_activities')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.title} ({self.project.title})"