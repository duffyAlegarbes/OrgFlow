from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path("", views.post_feed_view, name="feed"),
    path("create/", views.post_create_view, name="create"),
    path("edit/<int:post_id>/", views.post_edit_view, name="edit"),
    path("delete/<int:post_id>/", views.post_delete_view, name="delete"),
]