from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Organization(models.Model):
    CATEGORY_CHOICES = [
        ('Academic', 'Academic & Professional'),
        ('Leadership', 'Student Council & Leadership'),
        ('Cultural', 'Cultural & Arts'),
        ('Sports', 'Sports & Recreation'),
        ('Special Interest', 'Special Interest & Advocacy'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Pending', 'Pending Review'),
        ('Inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=200, unique=True, help_text="Official name of the organization")
    acronym = models.CharField(max_length=20, blank=True, help_text="e.g. SSG, CSS, HASBO")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Academic')
    description = models.TextField(help_text="Overview of the organization's mission and goals")
    logo = models.ImageField(upload_to="org_logos/", blank=True, null=True)
    contact_email = models.EmailField(blank=True, help_text="Official organization email for inquiries")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_organizations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.acronym:
            return f"{self.name} ({self.acronym})"
        return self.name


class OrganizationMembership(models.Model):
    ROLE_CHOICES = [
        ('President', 'President'),
        ('Officer', 'Executive Officer'),
        ('Member', 'General Member'),
        ('Adviser', 'Faculty Adviser'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active Member'),
        ('Pending', 'Pending Approval'),
        ('Rejected', 'Request Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'organization')
        ordering = ['-role', 'user__username']
        verbose_name = "Organization Membership"
        verbose_name_plural = "Organization Memberships"

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"