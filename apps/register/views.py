from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login:login")
        else:
            print("Form errors:", form.errors)
    else:
        form = UserCreationForm()
        
    return render(request, "register/register.html", {"form": form})