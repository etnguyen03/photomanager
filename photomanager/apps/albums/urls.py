from django.urls import path

from . import views

app_name = "albums"

urlpatterns = [
    path("<uuid:album_id>", views.view_album, name="display"),
    path(
        "<uuid:album_id>/share/<uuid:share_album_id>",
        views.view_album_share,
        name="share_display",
    ),
]
