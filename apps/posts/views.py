from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from apps.organizations.models import Organization, OrganizationMembership
from .models import Post, PartnershipRequest

@login_required(login_url='login:login')
def post_feed_view(request):
    """Campus-wide feed displaying announcements, events, and partnership requests."""
    posts = Post.objects.select_related(
        'organization', 'author', 'author__profile', 'partnership_details'
    ).order_by('-created_at')

    # Filtering
    post_type = request.GET.get('type', '').strip()
    org_slug = request.GET.get('org', '').strip()
    search_query = request.GET.get('search', '').strip()

    if post_type:
        posts = posts.filter(post_type=post_type)
    if org_slug:
        posts = posts.filter(organization__slug=org_slug)
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(organization__name__icontains=search_query)
        )

    # Check organizations where the current user is an active President or Officer
    officer_memberships = OrganizationMembership.objects.filter(
        user=request.user, status='Active', role__in=['President', 'Officer']
    ).select_related('organization')

    can_publish = officer_memberships.exists()
    
    # Pre-fetch org IDs where user is President (for moderation/delete permissions)
    president_org_ids = list(
        officer_memberships.filter(role='President').values_list('organization_id', flat=True)
    )

    return render(request, "posts/feed.html", {
        "posts": posts,
        "post_types": Post.POST_TYPE_CHOICES,
        "selected_type": post_type,
        "selected_org_slug": org_slug,
        "search_query": search_query,
        "can_publish": can_publish,
        "president_org_ids": president_org_ids,
        "all_orgs": Organization.objects.filter(status='Active'),
    })


@login_required(login_url='login:login')
def post_create_view(request):
    """Allows officers to publish posts under an organization they manage."""
    officer_memberships = OrganizationMembership.objects.filter(
        user=request.user, status='Active', role__in=['President', 'Officer']
    ).select_related('organization')

    if not officer_memberships.exists():
        messages.error(request, "Only organization officers can publish official posts or partnership requests.")
        return redirect("posts:feed")

    if request.method == "POST":
        org_id = request.POST.get("organization_id")
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        post_type = request.POST.get("post_type", "General")

        # Anti-Impersonation Check: Verify user is genuinely an active officer of the chosen org
        valid_membership = officer_memberships.filter(organization_id=org_id).first()
        if not valid_membership:
            messages.error(request, "Unauthorized organization selection. You cannot post on behalf of this organization.")
            return redirect("posts:create")

        if not title or not content:
            messages.error(request, "Post Title and Content are required.")
            return redirect("posts:create")

        # Create Post
        post = Post.objects.create(
            organization=valid_membership.organization,
            author=request.user,
            title=title,
            content=content,
            post_type=post_type,
        )

        # Create Partnership Details if Post Type is Partnership
        if post_type == 'Partnership':
            target_category = request.POST.get("target_category", "Any Organization").strip()
            PartnershipRequest.objects.create(
                post=post,
                target_category=target_category,
                status='Open'
            )

        messages.success(request, f"Post '{post.title}' published to the Campus Feed!")
        return redirect("posts:feed")

    # Optional pre-selection if navigated from a specific organization profile
    preselect_slug = request.GET.get('org', '')

    return render(request, "posts/create.html", {
        "officer_memberships": officer_memberships,
        "post_types": Post.POST_TYPE_CHOICES,
        "target_categories": Organization.CATEGORY_CHOICES,
        "preselect_slug": preselect_slug,
    })


@login_required(login_url='login:login')
def post_edit_view(request, post_id):
    """Allows the author or the organization's President to edit a post."""
    post = get_object_or_404(Post, id=post_id)

    is_president = OrganizationMembership.objects.filter(
        user=request.user, organization=post.organization, status='Active', role='President'
    ).exists()

    if post.author != request.user and not is_president:
        messages.error(request, "You do not have permission to edit this post.")
        return redirect("posts:feed")

    if request.method == "POST":
        post.title = request.POST.get("title", post.title).strip()
        post.content = request.POST.get("content", post.content).strip()
        post.save()

        # Update partnership status if applicable
        if post.post_type == 'Partnership' and hasattr(post, 'partnership_details'):
            partnership = post.partnership_details
            partnership.target_category = request.POST.get("target_category", partnership.target_category).strip()
            partnership.status = request.POST.get("partnership_status", partnership.status)
            partnership.save()

        messages.success(request, "Post updated successfully!")
        return redirect("posts:feed")

    return render(request, "posts/edit.html", {
        "post": post,
        "target_categories": Organization.CATEGORY_CHOICES,
        "partnership_statuses": PartnershipRequest.STATUS_CHOICES,
    })


@login_required(login_url='login:login')
def post_delete_view(request, post_id):
    """Allows the author or organization's President to delete a post."""
    post = get_object_or_404(Post, id=post_id)

    is_president = OrganizationMembership.objects.filter(
        user=request.user, organization=post.organization, status='Active', role='President'
    ).exists()

    if post.author != request.user and not is_president:
        messages.error(request, "You do not have permission to delete this post.")
        return redirect("posts:feed")

    post_title = post.title
    post.delete()
    messages.success(request, f"Post '{post_title}' deleted.")
    return redirect("posts:feed")