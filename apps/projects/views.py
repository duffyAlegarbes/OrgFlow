from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.organizations.models import Organization, OrganizationMembership
from .models import Project, ProjectActivity
from apps.notifications.models import Notification

@login_required(login_url='login:login')
def project_list_view(request, org_slug):
    """Lists all projects for an organization filtered by status."""
    org = get_object_or_404(Organization, slug=org_slug)

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active'
    ).first()

    is_officer = membership and membership.role in ['President', 'Officer']

    status_filter = request.GET.get('status', '').strip()
    projects = Project.objects.filter(organization=org)

    if status_filter:
        projects = projects.filter(status=status_filter)

    return render(request, "projects/list.html", {
        "org": org,
        "projects": projects.order_by('-created_at'),
        "membership": membership,
        "is_officer": is_officer,
        "status_filter": status_filter,
        "statuses": Project.STATUS_CHOICES,
        "total_projects": projects.count(),
    })


@login_required(login_url='login:login')
def project_detail_view(request, project_id):
    """Detailed view of a project with activities, milestones, and task assignment."""
    project = get_object_or_404(Project, id=project_id)
    org = project.organization

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active'
    ).first()

    is_officer = membership and membership.role in ['President', 'Officer']

    # Get active members for task delegation dropdown
    active_members = OrganizationMembership.objects.filter(
        organization=org, status='Active'
    ).select_related('user', 'user__profile')

    activities = project.activities.all().select_related('assigned_to', 'assigned_to__profile')
    total_activities = activities.count()
    completed_activities = activities.filter(status='Done').count()
    progress_percentage = int((completed_activities / total_activities * 100)) if total_activities > 0 else 0

    return render(request, "projects/detail.html", {
        "project": project,
        "org": org,
        "membership": membership,
        "is_officer": is_officer,
        "activities": activities,
        "active_members": active_members,
        "total_activities": total_activities,
        "completed_activities": completed_activities,
        "progress_percentage": progress_percentage,
        "statuses": Project.STATUS_CHOICES,
    })


@login_required(login_url='login:login')
def project_create_view(request, org_slug):
    """Allows officers to create a new project."""
    org = get_object_or_404(Organization, slug=org_slug)

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active', role__in=['President', 'Officer']
    ).first()

    if not membership:
        messages.error(request, "Only organization officers have permission to create projects.")
        return redirect("projects:list", org_slug=org.slug)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        status = request.POST.get("status", "Planning")
        date_start = request.POST.get("date_start") or None
        date_end = request.POST.get("date_end") or None
        budget = request.POST.get("budget_allocated") or 0.00

        if not title or not description:
            messages.error(request, "Project Title and Description are required.")
            return redirect("projects:create", org_slug=org.slug)

        project = Project.objects.create(
            organization=org,
            title=title,
            description=description,
            status=status,
            date_start=date_start,
            date_end=date_end,
            budget_allocated=budget,
            created_by=request.user,
        )

        messages.success(request, f"Project '{project.title}' created successfully!")
        return redirect("projects:detail", project_id=project.id)

    return render(request, "projects/create.html", {
        "org": org,
        "statuses": Project.STATUS_CHOICES
    })


@login_required(login_url='login:login')
def project_edit_view(request, project_id):
    """Allows officers to update project status, dates, and budget."""
    project = get_object_or_404(Project, id=project_id)
    org = project.organization

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active', role__in=['President', 'Officer']
    ).first()

    if not membership:
        messages.error(request, "You do not have permission to edit this project.")
        return redirect("projects:detail", project_id=project.id)

    if request.method == "POST":
        project.title = request.POST.get("title", project.title).strip()
        project.description = request.POST.get("description", project.description).strip()
        project.status = request.POST.get("status", project.status)
        project.date_start = request.POST.get("date_start") or None
        project.date_end = request.POST.get("date_end") or None
        project.budget_allocated = request.POST.get("budget_allocated") or 0.00
        project.save()

        messages.success(request, f"Project '{project.title}' updated successfully!")
        return redirect("projects:detail", project_id=project.id)

    return redirect("projects:detail", project_id=project.id)


@login_required(login_url='login:login')
def activity_add_view(request, project_id):
    """Allows officers to add sub-tasks/activities under a project."""
    project = get_object_or_404(Project, id=project_id)
    org = project.organization

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active', role__in=['President', 'Officer']
    ).first()

    if not membership:
        messages.error(request, "Only officers can delegate project activities.")
        return redirect("projects:detail", project_id=project.id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        assigned_user_id = request.POST.get("assigned_to")

        assigned_user = None
        if assigned_user_id:
            from django.contrib.auth.models import User
            assigned_user = User.objects.filter(id=assigned_user_id).first()

        if title:
            ProjectActivity.objects.create(
                project=project,
                title=title,
                assigned_to=assigned_user,
                status='Pending'
            )
            if assigned_user and assigned_user != request.user:
                Notification.objects.create(
                    recipient=assigned_user,
                    notification_type='Project Task',
                    message=f"You were assigned a new task '{title}' in project '{project.title}' ({org.name})."
                )
            messages.success(request, f"Activity '{title}' added to project!")

    return redirect("projects:detail", project_id=project.id)


@login_required(login_url='login:login')
def activity_toggle_view(request, activity_id):
    """Toggles task status between Pending and Done."""
    activity = get_object_or_404(ProjectActivity, id=activity_id)
    project = activity.project
    org = project.organization

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active'
    ).first()

    is_authorized = membership and (
        membership.role in ['President', 'Officer'] or activity.assigned_to == request.user
    )

    if not is_authorized:
        messages.error(request, "You are not authorized to update this activity.")
        return redirect("projects:detail", project_id=project.id)

    activity.status = 'Done' if activity.status == 'Pending' else 'Pending'
    activity.save()

    messages.info(request, f"Task marked as {activity.status}.")
    return redirect("projects:detail", project_id=project.id)