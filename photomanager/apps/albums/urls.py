from django.urls import path

from . import views

app_name = "albums"

urlpatterns = [
    path("", views.AlbumListView.as_view(), name="list"),
    path("create", views.AlbumCreateView.as_view(), name="create"),
    path("<uuid:album_id>", views.view_album, name="display"),
    path("<uuid:pk>/edit", views.AlbumEditView.as_view(), name="edit"),
    path("<uuid:pk>/delete", views.AlbumDeleteView.as_view(), name="delete"),
    path(
        "<uuid:album_id>/share/<uuid:share_album_id>",
        views.view_album_share,
        name="share_display",
    ),
    path(
        "<uuid:album_id>/share/links",
        views.AlbumShareLinkList.as_view(),
        name="share_links",
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
