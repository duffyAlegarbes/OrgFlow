from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.organizations.models import Organization, OrganizationMembership
from .models import StudentAgenda, KPITarget

@login_required(login_url='login:login')
def kpi_dashboard_view(request, org_slug):
    """Organization KPI workspace: View targets and recorded progress under each Student Agenda."""
    org = get_object_or_404(Organization, slug=org_slug)

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active'
    ).first()

    is_officer = membership and membership.role in ['President', 'Officer']

    # Retrieve all institutional student agendas
    agendas = StudentAgenda.objects.all().order_by('-academic_year', 'title')

    # Structure data: Group organization KPI targets by Agenda
    agenda_data = []
    total_targets = 0
    total_achieved_pct = 0

    for agenda in agendas:
        targets = KPITarget.objects.filter(organization=org, agenda=agenda)
        target_count = targets.count()
        total_targets += target_count

        agenda_progress = 0
        if target_count > 0:
            agenda_progress = int(sum(t.progress_percentage for t in targets) / target_count)
            total_achieved_pct += agenda_progress

        agenda_data.append({
            'agenda': agenda,
            'targets': targets,
            'progress': agenda_progress,
        })

    overall_progress = int(total_achieved_pct / agendas.count()) if agendas.count() > 0 else 0

    return render(request, "kpi/dashboard.html", {
        "org": org,
        "membership": membership,
        "is_officer": is_officer,
        "agenda_data": agenda_data,
        "total_targets": total_targets,
        "overall_progress": overall_progress,
    })


@login_required(login_url='login:login')
def kpi_target_create_view(request, org_slug):
    """Allows officers to add a measurable KPI target under an institutional Agenda."""
    org = get_object_or_404(Organization, slug=org_slug)

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active', role__in=['President', 'Officer']
    ).first()

    if not membership:
        messages.error(request, "Only officers can define KPI targets.")
        return redirect("kpi:dashboard", org_slug=org.slug)

    agendas = StudentAgenda.objects.all()

    if request.method == "POST":
        agenda_id = request.POST.get("agenda_id")
        metric_name = request.POST.get("metric_name", "").strip()
        target_value = request.POST.get("target_value")
        achieved_value = request.POST.get("achieved_value") or 0.00

        agenda = get_object_or_404(StudentAgenda, id=agenda_id)

        if not metric_name or not target_value:
            messages.error(request, "Metric name and target value are required.")
            return redirect("kpi:create", org_slug=org.slug)

        KPITarget.objects.create(
            organization=org,
            agenda=agenda,
            metric_name=metric_name,
            target_value=target_value,
            achieved_value=achieved_value,
        )

        messages.success(request, f"Target '{metric_name}' defined under {agenda.title}!")
        return redirect("kpi:dashboard", org_slug=org.slug)

    return render(request, "kpi/create.html", {
        "org": org,
        "agendas": agendas,
    })


@login_required(login_url='login:login')
def kpi_target_update_view(request, target_id):
    """Allows officers to log progress/results on an existing KPI."""
    target = get_object_or_404(KPITarget, id=target_id)
    org = target.organization

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active', role__in=['President', 'Officer']
    ).first()

    if not membership:
        messages.error(request, "Only officers can update progress records.")
        return redirect("kpi:dashboard", org_slug=org.slug)

    if request.method == "POST":
        achieved_value = request.POST.get("achieved_value")
        if achieved_value:
            target.achieved_value = achieved_value
            target.save()
            messages.success(request, f"Updated progress for '{target.metric_name}' to {achieved_value}!")

    return redirect("kpi:dashboard", org_slug=org.slug)

@login_required(login_url='login:login')
def sso_agendas_view(request):
    """SSO Staff: Create and manage institutional Student Agendas without /admin/."""
    if not request.user.is_staff:
        messages.error(request, "Access restricted to Student Success Office staff.")
        return redirect("home:home")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create_agenda":
            title = request.POST.get("title", "").strip()
            academic_year = request.POST.get("academic_year", "").strip()
            description = request.POST.get("description", "").strip()

            if not title or not academic_year or not description:
                messages.error(request, "Title, Academic Year, and Description are required.")
                return redirect("kpi:sso_agendas")

            StudentAgenda.objects.create(
                title=title,
                academic_year=academic_year,
                description=description,
            )
            messages.success(request, f"Student Agenda '{title}' published!")

        elif action == "delete_agenda":
            agenda_id = request.POST.get("agenda_id")
            agenda = get_object_or_404(StudentAgenda, id=agenda_id)
            agenda_title = agenda.title
            agenda.delete()
            messages.info(request, f"Removed Student Agenda '{agenda_title}'.")

        return redirect("kpi:sso_agendas")

    agendas = StudentAgenda.objects.all().order_by('-academic_year', 'title')
    return render(request, "kpi/sso_agendas.html", {
        "agendas": agendas,
    })