from django.urls import path
from . import views

app_name = "accreditation"

urlpatterns = [
    path("org/<slug:org_slug>/", views.org_accreditation_view, name="org_status"),
    path("org/<slug:org_slug>/attach/", views.attach_document_view, name="attach_doc"),
    path("org/<slug:org_slug>/submit/", views.submit_accreditation_view, name="submit"),
    path("sso/", views.sso_dashboard_view, name="sso_dashboard"),
    path("sso/review/<int:submission_id>/", views.sso_review_view, name="sso_review"),
]