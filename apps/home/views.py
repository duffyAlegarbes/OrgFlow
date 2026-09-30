from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.organizations.models import Organization, OrganizationMembership

@login_required(login_url='login:login')
def home_view(request):
    # 1. Query all active organizations the user belongs to
    user_memberships = OrganizationMembership.objects.filter(
        user=request.user, status='Active'
    ).select_related('organization')

    has_organizations = user_memberships.exists()

    selected_membership = None
    selected_org = None
    active_members_count = 0
    pending_requests_count = 0
    is_officer = False
    is_president = False

    if has_organizations:
        # Check if a specific organization was selected via query param (?org=slug)
        requested_org_slug = request.GET.get('org', '').strip()
        
        if requested_org_slug:
            selected_membership = user_memberships.filter(organization__slug=requested_org_slug).first()

        # Default to the user's first organization if none selected or invalid
        if not selected_membership:
            selected_membership = user_memberships.first()

        selected_org = selected_membership.organization
        
        # Determine leadership permissions in the selected organization
        is_officer = selected_membership.role in ['President', 'Officer']
        is_president = selected_membership.role == 'President'

        # Real-time metrics
        active_members_count = OrganizationMembership.objects.filter(
            organization=selected_org, status='Active'
        ).count()

        if is_officer:
            pending_requests_count = OrganizationMembership.objects.filter(
                organization=selected_org, status='Pending'
            ).count()

    context = {
        'has_organizations': has_organizations,
        'user_memberships': user_memberships,
        'selected_membership': selected_membership,
        'selected_org': selected_org,
        'active_members_count': active_members_count,
        'pending_requests_count': pending_requests_count,
        'is_officer': is_officer,
        'is_president': is_president,
        'total_orgs_joined': user_memberships.count(),
    }
    return render(request, "home/home.html", context)