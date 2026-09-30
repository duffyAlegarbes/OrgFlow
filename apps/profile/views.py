from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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

        # 2. Handle Academic Details Update
        elif "update_profile" in request.POST:
            full_name = request.POST.get("full_name", "").strip()
            email = request.POST.get("email", "").strip()
            bio = request.POST.get("bio", "").strip()

            # Update Profile Model
            profile.full_name = full_name
            profile.bio = bio
            profile.save()

            # Update User Institutional Email
            request.user.email = email
            request.user.save()

            messages.success(request, "Academic profile details updated successfully!")
            return redirect("profile:profile")

    return render(request, "profile/profile.html", {"profile": profile})