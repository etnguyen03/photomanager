from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
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
    """
    View for viewing a (private) album, but with a share link

    :param request: Request object
    :param album_id: Album ID (UUID)
    :param share_album_id: Share link ID (UUID)
    :return: HttpResponse or 404 if share link invalid
    """
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
    """View for editing the metadata on an album."""

    model = Album
    fields = ["name", "description", "publicly_accessible", "photos"]
    template_name_suffix = "_update"

    def get_success_url(self):
        return reverse_lazy("albums:display", kwargs={"album_id": self.kwargs["pk"]})

    def test_func(self) -> bool:
        """
        Used to ensure that only the owner of this album can modify it.

        :return: True if the owner of this album is the logged in user, false otherwise
        """
        return get_object_or_404(Album, id=self.kwargs["pk"]).owner == self.request.user


class AlbumCreateView(LoginRequiredMixin, CreateView):
    """View to create an album."""

    model = Album
    fields = ["name", "description", "publicly_accessible", "photos"]

    def get_success_url(self):
        return reverse_lazy("albums:display", kwargs={"album_id": self.object.id})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(AlbumCreateView, self).form_valid(form)


class AlbumListView(ListView):
    """View to list albums."""

    model = Album
    paginate_by = 25

    def get_queryset(self):
        # If the user isn't authenticated, then only the albums that are publicly accessible are visible
        if not self.request.user.is_authenticated:
            return Album.objects.filter(publicly_accessible=True).order_by(
                "-creation_time"
            )
        else:
            # Otherwise, only show the albums where the owner is the logged in user
            return Album.objects.filter(owner=self.request.user).order_by(
                "-creation_time"
            )


class AlbumDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View to handle deletion of an album, but not the photos within it."""

    model = Album
    success_url = reverse_lazy("albums:list")

    def test_func(self) -> bool:
        """
        Used to ensure that only the owner of this album can modify it.

        :return: True if the owner of this album is the logged in user, false otherwise
        """
        return get_object_or_404(Album, id=self.kwargs["pk"]).owner == self.request.user


@login_required
@require_POST
def album_share_link_create(request, album_id: str) -> HttpResponse:
    """
    View to handle the creation of share links for albums.

    :param request: Request object
    :param album_id: The album ID to create a link for
    :return: HttpResponse
    """
    album = get_object_or_404(Album, id=album_id)

    if request.user != album.owner:
        return HttpResponseForbidden()

    AlbumShareLink.objects.create(album=album, creator=request.user)

    messages.success(request, "Share link successfully created.")

    return redirect(reverse_lazy("albums:share_links", kwargs={"album_id": album_id}))


class AlbumShareLinkList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View to list AlbumShareLinks."""

    model = AlbumShareLink
    paginate_by = 25

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["album"] = get_object_or_404(Album, id=self.kwargs["album_id"])
        return context

    def test_func(self):
        return (
            get_object_or_404(Album, id=self.kwargs["album_id"]).owner
            == self.request.user
        )

    def get_queryset(self):
        return AlbumShareLink.objects.filter(
            album=get_object_or_404(Album, id=self.kwargs["album_id"])
        ).order_by("-creation_time")


class AlbumShareLinkDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View to handle the deletion of AlbumShareLinks."""

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
    """View to handle editing the metadata of AlbumShareLinks."""

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
