from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Organization, OrganizationMembership
from apps.notifications.models import Notification

@login_required(login_url='login:login')
def org_directory_view(request):
    query = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category', '').strip()

    organizations = Organization.objects.filter(status='Active')

    if query:
        organizations = organizations.filter(
            Q(name__icontains=query) | Q(acronym__icontains=query) | Q(description__icontains=query)
        )

    if selected_category:
        organizations = organizations.filter(category=selected_category)

    user_memberships = OrganizationMembership.objects.filter(
        user=request.user, status='Active'
    ).values_list('organization_id', flat=True)

    return render(request, "organizations/directory.html", {
        "organizations": organizations,
        "query": query,
        "selected_category": selected_category,
        "categories": Organization.CATEGORY_CHOICES,
        "total_count": organizations.count(),
        "user_org_ids": list(user_memberships)
    })


@login_required(login_url='login:login')
def org_detail_view(request, slug):
    org = get_object_or_404(Organization, slug=slug)

    membership = OrganizationMembership.objects.filter(user=request.user, organization=org).first()

    # Production ORM optimization: single JOIN query for user and profile
    active_members = OrganizationMembership.objects.filter(
        organization=org, status='Active'
    ).select_related('user', 'user__profile')

    is_officer = membership and membership.status == 'Active' and membership.role in ['President', 'Officer']
    is_president = membership and membership.status == 'Active' and membership.role == 'President'
    
    pending_count = 0
    if is_officer:
        pending_count = OrganizationMembership.objects.filter(organization=org, status='Pending').count()

    return render(request, "organizations/detail.html", {
        "org": org,
        "membership": membership,
        "active_members": active_members,
        "is_officer": is_officer,
        "is_president": is_president,
        "pending_count": pending_count,
    })


@login_required(login_url='login:login')
def org_create_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        acronym = request.POST.get("acronym", "").strip()
        category = request.POST.get("category", "Academic")
        contact_email = request.POST.get("contact_email", "").strip()
        description = request.POST.get("description", "").strip()
        logo = request.FILES.get("logo")

        if not name or not description:
            messages.error(request, "Organization Name and Description are required.")
            return redirect("organizations:create")

        if Organization.objects.filter(name__iexact=name).exists():
            messages.error(request, f"An organization named '{name}' already exists.")
            return redirect("organizations:create")

        # 1. Create Organization
        org = Organization.objects.create(
            name=name,
            acronym=acronym,
            category=category,
            contact_email=contact_email,
            description=description,
            logo=logo,
            created_by=request.user,
            status='Active'
        )

        # 2. Auto-assign Creator as President with Active status
        OrganizationMembership.objects.create(
            user=request.user,
            organization=org,
            role='President',
            status='Active'
        )

        messages.success(request, f"Organization '{org.name}' created! You have been assigned as President.")
        return redirect("organizations:detail", slug=org.slug)

    return render(request, "organizations/create.html", {
        "categories": Organization.CATEGORY_CHOICES
    })


@login_required(login_url='login:login')
def org_join_view(request, slug):
    """Submits a membership request to an organization."""
    org = get_object_or_404(Organization, slug=slug)

    membership, created = OrganizationMembership.objects.get_or_create(
        user=request.user,
        organization=org,
        defaults={'role': 'Member', 'status': 'Pending'}
    )

    if not created:
        if membership.status == 'Active':
            messages.info(request, "You are already an active member of this organization.")
        elif membership.status == 'Pending':
            messages.info(request, "Your membership request is already pending review.")
        elif membership.status == 'Rejected':
            membership.status = 'Pending'
            membership.save()
            messages.success(request, "Your membership request has been re-submitted for review.")
    else:
        messages.success(request, f"Membership request submitted to {org.name}! Awaiting officer approval.")

    return redirect("organizations:detail", slug=org.slug)


@login_required(login_url='login:login')
def org_leave_view(request, slug):
    """Allows a member to leave an organization."""
    org = get_object_or_404(Organization, slug=slug)
    membership = get_object_or_404(OrganizationMembership, user=request.user, organization=org)

    if membership.role == 'President':
        # Safety check: prevent leaving if sole President
        presidents_count = OrganizationMembership.objects.filter(
            organization=org, role='President', status='Active'
        ).count()
        if presidents_count <= 1:
            messages.error(request, "As the sole President, you cannot leave the organization without appointing a new President.")
            return redirect("organizations:detail", slug=org.slug)

    membership.delete()
    messages.success(request, f"You have left {org.name}.")
    return redirect("organizations:directory")


@login_required(login_url='login:login')
def manage_members_view(request, slug):
    """Officer dashboard for reviewing requests, assigning roles, and managing members."""
    org = get_object_or_404(Organization, slug=slug)

    # Permission check: User MUST be an active President or Officer
    officer_membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active', role__in=['President', 'Officer']
    ).first()

    if not officer_membership:
        messages.error(request, "You do not have administrative permission to manage this organization's members.")
        return redirect("organizations:detail", slug=org.slug)

    is_president = officer_membership.role == 'President'

    # 1. Handle Role Updates & Member Removal (President Only)
    if request.method == "POST":
        action = request.POST.get("action")
        target_membership_id = request.POST.get("membership_id")
        target_membership = get_object_or_404(OrganizationMembership, id=target_membership_id, organization=org)

        if action == "update_role" and is_president:
            new_role = request.POST.get("new_role")
            if new_role in ['President', 'Officer', 'Member', 'Adviser']:
                target_membership.role = new_role
                target_membership.save()
                messages.success(request, f"Updated {target_membership.user.username}'s role to {new_role}.")

        elif action == "remove_member" and is_president:
            if target_membership.user == request.user:
                messages.error(request, "You cannot remove yourself from this panel.")
            else:
                target_membership.delete()
                messages.success(request, f"Removed {target_membership.user.username} from the organization.")

        elif action == "approve_request":
            target_membership.status = 'Active'
            target_membership.save()
            Notification.objects.create(
                recipient=target_membership.user,
                notification_type='Membership',
                message=f"Welcome! Your request to join {org.name} has been approved."
            )
            messages.success(request, f"Approved {target_membership.user.username}'s membership!")

        elif action == "reject_request":
            target_membership.status = 'Rejected'
            target_membership.save()
            Notification.objects.create(
                recipient=target_membership.user,
                notification_type='Membership',
                message=f"Update: Your request to join {org.name} was declined."
            )
            messages.info(request, f"Rejected {target_membership.user.username}'s membership request.")

        return redirect("organizations:manage_members", slug=org.slug)

    # Queries
    active_members = OrganizationMembership.objects.filter(
        organization=org, status='Active'
    ).select_related('user', 'user__profile')
    
    pending_requests = OrganizationMembership.objects.filter(
        organization=org, status='Pending'
    ).select_related('user', 'user__profile')

    return render(request, "organizations/manage_members.html", {
        "org": org,
        "is_president": is_president,
        "active_members": active_members,
        "pending_requests": pending_requests,
        "roles": OrganizationMembership.ROLE_CHOICES,
    })