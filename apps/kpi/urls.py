from django.urls import path
from . import views

app_name = "kpi"

urlpatterns = [
    path("org/<slug:org_slug>/", views.kpi_dashboard_view, name="dashboard"),
    path("org/<slug:org_slug>/create/", views.kpi_target_create_view, name="create"),
    path("target/<int:target_id>/update/", views.kpi_target_update_view, name="update"),
]