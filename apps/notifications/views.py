from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification

@login_required(login_url='login:login')
def notification_list_view(request):
    """Displays the authenticated user's notification inbox."""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    return render(request, "notifications/list.html", {
        "notifications": notifications,
        "unread_count": unread_count,
    })

@login_required(login_url='login:login')
def mark_read_view(request, notif_id):
    """Marks a specific notification as read (Strictly verified by recipient)."""
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    return redirect("notifications:list")

@login_required(login_url='login:login')
def mark_all_read_view(request):
    """Marks all unread notifications for the logged-in user as read."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect("notifications:list")