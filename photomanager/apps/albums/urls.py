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
    path(
        "<uuid:album_id>/share/links", views.album_share_link_list, name="share_links"
    ),
    path(
        "<uuid:album_id>/share/links/create",
        views.album_share_link_create,
        name="share_links_create",
    ),
    path(
        "<uuid:album_id>/share/links/delete/<uuid:pk>",
        views.AlbumShareLinkDelete.as_view(),
        name="share_links_delete",
    ),
    path(
        "<uuid:album_id>/share/links/edit/<uuid:pk>",
        views.AlbumShareLinkEdit.as_view(),
        name="share_links_edit",
    ),
]
