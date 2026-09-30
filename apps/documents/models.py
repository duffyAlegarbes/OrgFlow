from django.db import models
from django.contrib.auth.models import User
from apps.organizations.models import Organization

class Document(models.Model):
    CATEGORY_CHOICES = [
        ('CBL', 'Constitution & By-Laws'),
        ('Financial', 'Financial Report'),
        ('Proposal', 'Project Proposal'),
        ('Minutes', 'Meeting Minutes'),
        ('Documentation', 'Activity Documentation'),
        ('Other', 'Other Document'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='org_documents/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    is_public = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.organization.acronym or self.organization.name})"