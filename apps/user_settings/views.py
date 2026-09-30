from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import UserSettings

@login_required(login_url='login:login')
def settings_view(request):
    settings_obj, created = UserSettings.objects.get_or_create(user=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == "POST":
        # 1. Handle Preferences Update
        if "save_preferences" in request.POST:
            dark_mode = request.POST.get("dark_mode") == "on"
            email_notifications = request.POST.get("email_notifications") == "on"

            settings_obj.dark_mode = dark_mode
            settings_obj.email_notifications = email_notifications
            settings_obj.save()

            messages.success(request, "Preferences have been saved successfully!")
            return redirect("user_settings:settings")

        # 2. Handle Password Change
        elif "change_password" in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # Keep user logged in after password change
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was successfully updated!")
                return redirect("user_settings:settings")
            else:
                messages.error(request, "Please correct the errors in the password form below.")

    return render(request, "user_settings/settings.html", {
        "settings": settings_obj,
        "password_form": password_form
    })