from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from photomanager.apps.albums.models import Album, AlbumShareLink


def view_album(request, album_id: str) -> HttpResponse:
    """
    View for viewing an album.

    :param request: Request object
    :param album_id: ID of an album (a UUID)
    :return: an HTTP response
    """
    album = get_object_or_404(Album, id=album_id)

    if not album.publicly_accessible:
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
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


class AlbumEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Album
    fields = ["name", "description", "publicly_accessible", "photos"]
    template_name_suffix = "_update"

    def get_success_url(self):
        return reverse_lazy("albums:display", kwargs={"album_id": self.kwargs["pk"]})

    def test_func(self):
        return get_object_or_404(Album, id=self.kwargs["pk"]).owner == self.request.user


class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    fields = ["name", "description", "publicly_accessible", "photos"]

    def get_success_url(self):
        return reverse_lazy("albums:display", kwargs={"album_id": self.object.id})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(AlbumCreateView, self).form_valid(form)


class AlbumListView(ListView):
    model = Album
    paginate_by = 25

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Album.objects.filter(publicly_accessible=True).order_by(
                "-creation_time"
            )
        else:
            return Album.objects.filter(owner=self.request.user).order_by(
                "-creation_time"
            )


class AlbumDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Album
    success_url = reverse_lazy("albums:list")

    def test_func(self):
        return get_object_or_404(Album, id=self.kwargs["pk"]).owner == self.request.user


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
