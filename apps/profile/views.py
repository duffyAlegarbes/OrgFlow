from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile

@login_required(login_url='login:login')
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # 1. Handle Profile Image Upload
        if "profile_image" in request.FILES:
            profile.profile_image = request.FILES["profile_image"]
            profile.save()
            messages.success(request, "Profile photo updated successfully!")
            return redirect("profile:profile")

        # 2. Handle Text Details & Username Update
        elif "update_profile" in request.POST:
            new_username = request.POST.get("username", "").strip()
            full_name = request.POST.get("full_name", "").strip()
            bio = request.POST.get("bio", "").strip()
            email = request.POST.get("email", "").strip()

            # Validation: Username cannot be blank
            if not new_username:
                messages.error(request, "Username cannot be empty.")
                return redirect("profile:profile")

            # Validation: Check if the username is taken by another account
            if User.objects.exclude(pk=request.user.pk).filter(username=new_username).exists():
                messages.error(request, f"The username '{new_username}' is already taken. Please choose another.")
                return redirect("profile:profile")

            # Update User Model (Username & Email)
            request.user.username = new_username
            request.user.email = email
            request.user.save()

            # Update Profile Model (Full Name & Bio)
            profile.full_name = full_name
            profile.bio = bio
            profile.save()

            messages.success(request, "Profile and username updated successfully!")
            return redirect("profile:profile")

    return render(request, "profile/profile.html", {"profile": profile})