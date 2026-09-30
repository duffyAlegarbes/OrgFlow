from django.urls import path
from . import views

app_name = "organizations"

urlpatterns = [
    path("", views.org_directory_view, name="directory"),
    path("create/", views.org_create_view, name="create"),
    path("<slug:slug>/", views.org_detail_view, name="detail"),
    path("<slug:slug>/join/", views.org_join_view, name="join"),
    path("<slug:slug>/leave/", views.org_leave_view, name="leave"),
    path("<slug:slug>/manage-members/", views.manage_members_view, name="manage_members"),
]