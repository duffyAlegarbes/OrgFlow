from django.db import models
from django.contrib.auth.models import User
from apps.organizations.models import Organization

class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('Announcement', 'Official Announcement'),
        ('Event', 'Event Update'),
        ('Partnership', 'Partnership Request'),
        ('General', 'General Post'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=30, choices=POST_TYPE_CHOICES, default='General')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.organization.name}"

class PartnershipRequest(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open for Collaboration'),
        ('Closed', 'Closed'),
    ]

    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='partnership_details')
    target_category = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')

    def __str__(self):
        return f"Partnership: {self.post.title} ({self.status})"