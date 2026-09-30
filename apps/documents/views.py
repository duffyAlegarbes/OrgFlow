from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from apps.organizations.models import Organization, OrganizationMembership
from .models import Document

@login_required(login_url='login:login')
def document_list_view(request, org_slug):
    """Displays the categorized document repository for an organization."""
    org = get_object_or_404(Organization, slug=org_slug)

    # Check user's membership status in this organization
    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active'
    ).first()

    is_member = membership is not None
    is_officer = is_member and membership.role in ['President', 'Officer']

    # Filter documents
    documents = Document.objects.filter(organization=org)
    
    # Non-members only see public documents
    if not is_member:
        documents = documents.filter(is_public=True)

    # Category and Search filters
    category = request.GET.get('category', '').strip()
    search_query = request.GET.get('search', '').strip()

    if category:
        documents = documents.filter(category=category)
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) | Q(category__icontains=search_query)
        )

    return render(request, "documents/list.html", {
        "org": org,
        "documents": documents.order_by('-uploaded_at'),
        "membership": membership,
        "is_officer": is_officer,
        "is_member": is_member,
        "categories": Document.CATEGORY_CHOICES,
        "selected_category": category,
        "search_query": search_query,
        "total_count": documents.count(),
    })


@login_required(login_url='login:login')
def document_upload_view(request, org_slug):
    """Handles secure file uploads by organization officers."""
    org = get_object_or_404(Organization, slug=org_slug)

    # Permission check: Only active Officers and Presidents can upload
    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active', role__in=['President', 'Officer']
    ).first()

    if not membership:
        messages.error(request, "Only organization officers have permission to upload official documents.")
        return redirect("documents:list", org_slug=org.slug)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "Other")
        is_public = request.POST.get("is_public") == "on"
        file = request.FILES.get("file")

        if not title or not file:
            messages.error(request, "Document title and a file upload are required.")
            return redirect("documents:list", org_slug=org.slug)

        Document.objects.create(
            organization=org,
            uploaded_by=request.user,
            title=title,
            category=category,
            file=file,
            is_public=is_public,
        )

        messages.success(request, f"Document '{title}' successfully uploaded to the repository!")
        return redirect("documents:list", org_slug=org.slug)

    return redirect("documents:list", org_slug=org.slug)


@login_required(login_url='login:login')
def document_delete_view(request, doc_id):
    """Deletes a document with strict ownership/President permissions."""
    doc = get_object_or_404(Document, id=doc_id)
    org = doc.organization

    membership = OrganizationMembership.objects.filter(
        user=request.user, organization=org, status='Active'
    ).first()

    # Can delete if user is President, or if user is an Officer who uploaded this specific file
    can_delete = membership and (
        membership.role == 'President' or 
        (membership.role == 'Officer' and doc.uploaded_by == request.user)
    )

    if not can_delete:
        messages.error(request, "You do not have permission to delete this document.")
        return redirect("documents:list", org_slug=org.slug)

    doc_title = doc.title
    doc.delete()
    messages.success(request, f"Document '{doc_title}' was successfully removed.")
    return redirect("documents:list", org_slug=org.slug)