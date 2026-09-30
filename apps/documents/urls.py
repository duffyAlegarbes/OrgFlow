from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    path("<slug:org_slug>/", views.document_list_view, name="list"),
    path("<slug:org_slug>/upload/", views.document_upload_view, name="upload"),
    path("delete/<int:doc_id>/", views.document_delete_view, name="delete"),
]