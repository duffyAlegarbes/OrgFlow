from django.db import models
from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.documents.models import Document

class AccreditationCycle(models.Model):
    academic_year = models.CharField(max_length=20, help_text="e.g. 2024-2025")
    title = models.CharField(max_length=150)
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.academic_year})"

class AccreditationRequirement(models.Model):
    cycle = models.ForeignKey(AccreditationCycle, on_delete=models.CASCADE, related_name='requirements')
    title = models.CharField(max_length=150)
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} [{self.cycle.academic_year}]"

class AccreditationSubmission(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('Requires Revision', 'Requires Revision'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='accreditation_submissions')
    cycle = models.ForeignKey(AccreditationCycle, on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accreditation_submissions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_submissions')
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.organization.name} - {self.cycle.academic_year} ({self.status})"

class SubmittedDocument(models.Model):
    submission = models.ForeignKey(AccreditationSubmission, on_delete=models.CASCADE, related_name='submitted_documents')
    requirement = models.ForeignKey(AccreditationRequirement, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.submission.organization.name} - {self.requirement.title}"