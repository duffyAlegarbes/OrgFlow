from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login:login')
def home_view(request):
    # Context data for OrgFlow Dashboard
    context = {
        'org_name': 'Computer Science Student Council',
        'active_members': 42,
        'upcoming_activities_count': 3,
        'remaining_budget': 15500.00,
        'recent_announcement': 'General Assembly meeting scheduled for Friday at 3 PM in Room 402.',
    }
    return render(request, "home/home.html", context)