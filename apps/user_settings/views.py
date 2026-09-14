from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserSettings

@login_required(login_url='login:login')
def settings_view(request):
    settings_obj, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Capture form values
        dark_mode = request.POST.get("dark_mode") == "on"
        email_notifications = request.POST.get("email_notifications") == "on"

        # Update and save to Supabase
        settings_obj.dark_mode = dark_mode
        settings_obj.email_notifications = email_notifications
        settings_obj.save()

        messages.success(request, "Preferences and settings have been saved successfully!")
        return redirect("user_settings:settings")

    return render(request, "user_settings/settings.html", {"settings": settings_obj})