from django.urls import path

from . import views

app_name = "albums"

urlpatterns = [
    path("<uuid:album_id>", views.view_album, name="display"),
]
