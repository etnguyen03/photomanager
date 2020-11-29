from django.urls import path

from . import views

app_name = "photos"

urlpatterns = [
    path("rescan", views.rescan_directory, name="rescan"),
    path("reprocess/<uuid:image_id>", views.reprocess_file, name="reprocess"),
    path("raw_image/<uuid:image_id>", views.get_raw_image, name="raw_image"),
    path("image/<uuid:image_id>", views.view_single_photo, name="view_single_photo"),
]
