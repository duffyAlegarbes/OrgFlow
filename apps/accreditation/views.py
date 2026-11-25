from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.organizations.models import Organization, OrganizationMembership
from apps.documents.models import Document
from apps.notifications.models import Notification
from .models import (
    AccreditationCycle,
    AccreditationRequirement,
    AccreditationSubmission,
    SubmittedDocument
)

@login_required(login_url='login:login')
def org_accreditation_view(request, org_slug):
    """Officer interface: View requirements, attach documents, and submit application."""
    org = get_object_or_404(Organization, slug=org_slug)

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active'
    ).first()

    is_officer = membership and membership.role in ['President', 'Officer']

    # Get the currently active accreditation cycle
    active_cycle = AccreditationCycle.objects.filter(is_active=True).first()

    submission = None
    requirements_data = []
    missing_mandatory = 0

    if active_cycle:
        # Get or create submission for this org and cycle
        submission, _ = AccreditationSubmission.objects.get_or_create(
            organization=org,
            cycle=active_cycle,
            defaults={'submitted_by': request.user, 'status': 'Draft'}
        )

        requirements = active_cycle.requirements.all()
        submitted_docs_map = {
            sd.requirement_id: sd.document
            for sd in submission.submitted_documents.select_related('document')
        }

        for req in requirements:
            attached_doc = submitted_docs_map.get(req.id)
            if req.is_mandatory and not attached_doc:
                missing_mandatory += 1
            requirements_data.append({
                'requirement': req,
                'attached_doc': attached_doc,
            })

    # Available documents from org repository for attachment
    available_documents = Document.objects.filter(organization=org)

    return render(request, "accreditation/org_status.html", {
        "org": org,
        "is_officer": is_officer,
        "active_cycle": active_cycle,
        "submission": submission,
        "requirements_data": requirements_data,
        "missing_mandatory": missing_mandatory,
        "available_documents": available_documents,
    })


@login_required(login_url='login:login')
def attach_document_view(request, org_slug):
    """Attaches a repository document to a specific accreditation requirement."""
    org = get_object_or_404(Organization, slug=org_slug)

    # Permission check: Officers only
    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active', role__in=['President', 'Officer']
    ).first()

    if not membership:
        messages.error(request, "Only officers can attach accreditation documents.")
        return redirect("accreditation:org_status", org_slug=org.slug)

    if request.method == "POST":
        requirement_id = request.POST.get("requirement_id")
        document_id = request.POST.get("document_id")

        active_cycle = AccreditationCycle.objects.filter(is_active=True).first()
        submission = get_object_or_404(AccreditationSubmission, organization=org, cycle=active_cycle)
        requirement = get_object_or_404(AccreditationRequirement, id=requirement_id, cycle=active_cycle)
        document = get_object_or_404(Document, id=document_id, organization=org)

        if submission.status in ['Submitted', 'Approved']:
            messages.error(request, "Cannot modify documents while submission is under review or approved.")
            return redirect("accreditation:org_status", org_slug=org.slug)

        # Attach or update
        submitted_doc, created = SubmittedDocument.objects.get_or_create(
            submission=submission,
            requirement=requirement,
            defaults={'document': document}
        )
        if not created:
            submitted_doc.document = document
            submitted_doc.save()

        messages.success(request, f"Attached '{document.title}' to '{requirement.title}'.")

    return redirect("accreditation:org_status", org_slug=org.slug)


@login_required(login_url='login:login')
def submit_accreditation_view(request, org_slug):
    """Submits the accreditation package to the Student Success Office."""
    org = get_object_or_404(Organization, slug=org_slug)

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active', role__in=['President', 'Officer']
    ).first()

    if not membership:
        messages.error(request, "Only officers can submit accreditation applications.")
        return redirect("accreditation:org_status", org_slug=org.slug)

    active_cycle = get_object_or_404(AccreditationCycle, is_active=True)
    submission = get_object_or_404(AccreditationSubmission, organization=org, cycle=active_cycle)

    # Check that all mandatory requirements are fulfilled
    mandatory_req_ids = active_cycle.requirements.filter(is_mandatory=True).values_list('id', flat=True)
    attached_req_ids = submission.submitted_documents.values_list('requirement_id', flat=True)

    unmet = set(mandatory_req_ids) - set(attached_req_ids)
    if unmet:
        messages.error(request, "You cannot submit until all mandatory requirements have attached documents.")
        return redirect("accreditation:org_status", org_slug=org.slug)

    submission.status = 'Submitted'
    submission.submitted_by = request.user
    submission.save()

    messages.success(request, "Accreditation application submitted successfully to the Student Success Office!")
    return redirect("accreditation:org_status", org_slug=org.slug)


@login_required(login_url='login:login')
def sso_dashboard_view(request):
    """Student Success Office Desk: Lists all submissions across organizations."""
    if not request.user.is_staff:
        messages.error(request, "Access restricted to Student Success Office staff.")
        return redirect("home:home")

    active_cycle = AccreditationCycle.objects.filter(is_active=True).first()
    submissions = AccreditationSubmission.objects.all().select_related('organization', 'cycle', 'submitted_by')

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        submissions = submissions.filter(status=status_filter)

    return render(request, "accreditation/sso_dashboard.html", {
        "active_cycle": active_cycle,
        "submissions": submissions.order_by('-cycle__academic_year', 'organization__name'),
        "status_filter": status_filter,
        "statuses": AccreditationSubmission.STATUS_CHOICES,
    })


@login_required(login_url='login:login')
def sso_review_view(request, submission_id):
    """Student Success Office: Review submitted paperwork and grant approval / request revisions."""
    if not request.user.is_staff:
        messages.error(request, "Access restricted to Student Success Office staff.")
        return redirect("home:home")

    submission = get_object_or_404(AccreditationSubmission, id=submission_id)
    submitted_docs = submission.submitted_documents.select_related('requirement', 'document')

    if request.method == "POST":
        action = request.POST.get("action")
        remarks = request.POST.get("remarks", "").strip()

        if action == "approve":
            submission.status = 'Approved'
            submission.organization.status = 'Active'
            submission.organization.save()
            messages.success(request, f"Accreditation granted for {submission.organization.name}!")
        elif action == "revision":
            submission.status = 'Requires Revision'
            messages.info(request, f"Revision requested for {submission.organization.name}.")
        elif action == "reject":
            submission.status = 'Rejected'
            messages.warning(request, f"Accreditation application rejected for {submission.organization.name}.")

        submission.remarks = remarks
        submission.reviewed_by = request.user
        submission.save()

        if submission.submitted_by:
            Notification.objects.create(
                recipient=submission.submitted_by,
                notification_type='Accreditation',
                message=f"SSO Update for {submission.organization.name} ({submission.cycle.academic_year}): Your accreditation status is now '{submission.status}'."
            )

        return redirect("accreditation:sso_dashboard")

    return render(request, "accreditation/sso_review.html", {
        "submission": submission,
        "submitted_docs": submitted_docs,
    })

@login_required(login_url='login:login')
def sso_cycles_view(request):
    """SSO Staff: Create/activate accreditation cycles and manage requirements without /admin/."""
    if not request.user.is_staff:
        messages.error(request, "Access restricted to Student Success Office staff.")
        return redirect("home:home")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create_cycle":
            title = request.POST.get("title", "").strip()
            academic_year = request.POST.get("academic_year", "").strip()
            start_date = request.POST.get("start_date")
            is_active = request.POST.get("is_active") == "on"

            if not title or not academic_year or not start_date:
                messages.error(request, "Title, Academic Year, and Start Date are required.")
                return redirect("accreditation:sso_cycles")

            if is_active:
                # Ensure only one cycle is active at a time
                AccreditationCycle.objects.update(is_active=False)

            cycle = AccreditationCycle.objects.create(
                title=title,
                academic_year=academic_year,
                start_date=start_date,
                is_active=is_active,
            )
            messages.success(request, f"Accreditation Cycle '{cycle.title}' created!")

        elif action == "activate_cycle":
            cycle_id = request.POST.get("cycle_id")
            cycle = get_object_or_404(AccreditationCycle, id=cycle_id)
            AccreditationCycle.objects.update(is_active=False)
            cycle.is_active = True
            cycle.save()
            messages.success(request, f"'{cycle.title} ({cycle.academic_year})' is now the active accreditation cycle.")

        elif action == "add_requirement":
            cycle_id = request.POST.get("cycle_id")
            req_title = request.POST.get("req_title", "").strip()
            is_mandatory = request.POST.get("is_mandatory") == "on"

            cycle = get_object_or_404(AccreditationCycle, id=cycle_id)
            if not req_title:
                messages.error(request, "Requirement title cannot be empty.")
                return redirect("accreditation:sso_cycles")

            AccreditationRequirement.objects.create(
                cycle=cycle,
                title=req_title,
                is_mandatory=is_mandatory,
            )
            messages.success(request, f"Added requirement '{req_title}' to {cycle.academic_year}.")

        elif action == "delete_requirement":
            req_id = request.POST.get("requirement_id")
            req = get_object_or_404(AccreditationRequirement, id=req_id)
            req_title = req.title
            req.delete()
            messages.info(request, f"Removed requirement '{req_title}'.")

        return redirect("accreditation:sso_cycles")

    cycles = AccreditationCycle.objects.prefetch_related('requirements').order_by('-start_date', '-id')

    return render(request, "accreditation/sso_cycles.html", {
        "cycles": cycles,
    })