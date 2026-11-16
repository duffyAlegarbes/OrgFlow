from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("org/<slug:org_slug>/", views.project_list_view, name="list"),
    path("org/<slug:org_slug>/create/", views.project_create_view, name="create"),
    path("detail/<int:project_id>/", views.project_detail_view, name="detail"),
    path("detail/<int:project_id>/edit/", views.project_edit_view, name="edit"),
    path("detail/<int:project_id>/activity/add/", views.activity_add_view, name="activity_add"),
    path("activity/<int:activity_id>/toggle/", views.activity_toggle_view, name="activity_toggle"),
]