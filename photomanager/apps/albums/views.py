from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, UpdateView

from photomanager.apps.albums.models import Album, AlbumShareLink


@login_required
def view_album(request, album_id: str) -> HttpResponse:
    """
    View for viewing an album.

    :param request: Request object
    :param album_id: ID of an album (a UUID)
    :return: an HTTP response
    """
    album = get_object_or_404(Album, id=album_id)

    if album.owner != request.user:
        return HttpResponseForbidden()

    context = {
        "album": album,
        "photos": album.photos.all().order_by("photo_taken_time"),
    }

    return render(request, "albums/view_single_album.html", context=context)


def view_album_share(request, album_id: str, share_album_id: str) -> HttpResponse:
    album_share_link = get_object_or_404(
        AlbumShareLink, id=share_album_id, album__id=album_id
    )

    album = album_share_link.album

    context = {
        "album": album,
        "photos": album.photos.all().order_by("photo_taken_time"),
        "album_share_id": share_album_id,
    }

    return render(request, "albums/view_single_album.html", context=context)


@login_required
def album_share_link_create(request, album_id: str) -> HttpResponse:
    album = get_object_or_404(Album, id=album_id)

    if request.user != album.owner:
        return HttpResponseForbidden()

    AlbumShareLink.objects.create(album=album, creator=request.user)

    messages.success(request, "Share link successfully created.")

    return redirect(reverse_lazy("albums:share_links", kwargs={"album_id": album_id}))


@login_required
def album_share_link_list(request, album_id: str) -> HttpResponse:
    album = get_object_or_404(Album, id=album_id)

    if request.user != album.owner:
        return HttpResponseForbidden()

    context = {
        "album": album,
        "share_links": AlbumShareLink.objects.filter(album__id=album_id),
    }

    return render(request, "albums/list_share_links.html", context=context)


class AlbumShareLinkDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AlbumShareLink

    def get_success_url(self):
        return reverse_lazy(
            "albums:share_links", kwargs={"album_id": self.kwargs["album_id"]}
        )

    def test_func(self):
        return (
            get_object_or_404(AlbumShareLink, id=self.kwargs["pk"]).album.owner
            == self.request.user
        )


class AlbumShareLinkEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AlbumShareLink
    fields = ["description"]
    template_name_suffix = "_update"

    def get_success_url(self):
        return reverse_lazy(
            "albums:share_links", kwargs={"album_id": self.kwargs["album_id"]}
        )

    def test_func(self):
        return (
            get_object_or_404(AlbumShareLink, id=self.kwargs["pk"]).album.owner
            == self.request.user
        )
