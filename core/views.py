from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home_view(request):
    # Context data passed from View to UI/UX component
    context = {
        'org_name': 'Computer Science Student Council',
        'active_members': 42,
        'upcoming_activities_count': 3,
        'remaining_budget': 15500.00,
        'recent_announcement': 'General Assembly meeting scheduled for Friday at 3 PM in Room 402.',
    }
    return render(request, 'core/home.html', context)