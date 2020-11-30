from django.urls import path

from . import views

app_name = "photos"

urlpatterns = [
    path("rescan", views.rescan_directory, name="rescan"),
    path("reprocess/<uuid:image_id>", views.reprocess_file, name="reprocess"),
    path("raw_image/<uuid:image_id>", views.get_raw_image, name="raw_image"),
    path(
        "raw_image/<uuid:image_id>/album_share/<uuid:album_share_id>",
        views.get_raw_image_album_share,
        name="raw_image_album_share",
    ),
    path("<uuid:image_id>", views.view_single_photo, name="view_single_photo"),
    path(
        "<uuid:image_id>/album_share/<uuid:album_share_id>",
        views.view_single_photo_album_share,
        name="view_single_photo_album_share",
    ),
    path("update/<uuid:pk>", views.PhotoUpdate.as_view(), name="update_photo"),
]
