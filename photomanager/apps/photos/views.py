import base64
import io
import json
import os
import subprocess
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from hurry.filesize import size

from ..albums.models import Album, AlbumShareLink
from .models import Photo
from .tasks import process_image, scan_dir_for_changes


@login_required
def rescan_directory(request):
    scan_dir_for_changes.delay(request.user.subdirectory, request.user.username)
    return HttpResponse("OK")


@login_required
@require_POST
def reprocess_file(request, image_id):
    photo = get_object_or_404(Photo, id=image_id)

    if photo.user != request.user:
        return HttpResponseForbidden()

    process_image.delay(photo.id)
    messages.success(request, "EXIF metadata refresh queued.")
    return redirect(
        reverse_lazy("photos:view_single_photo", kwargs={"image_id": photo.id})
    )


def _get_raw_image(request, photo: Photo) -> FileResponse:
    """
    Backend method for getting a raw image.

    :param request: Request object
    :param photo: Photo object
    :return: FileResponse
    """
    # Read file
    READ_FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "utils/files/read_file.py",
    )

    # If this is a thumbnail we are reading, we will want to use a
    # different file path than if we are reading the actual file

    if request.GET.get("thumbnail"):
        file_to_read = os.path.join(
            settings.IMAGE_THUMBS_DIR,
            str(photo.id)[0],
            str(photo.id)[1],
            f"{str(photo.id)}.thumb.jpeg",
        )
    else:
        file_to_read = photo.file

    file_read: dict = json.loads(
        subprocess.run(
            (["sudo"] if os.getuid() != 0 else [])
            + [
                "pipenv",
                "run",
                "python3",
                READ_FILE_PATH,
                file_to_read,
            ],  # sudo required for chroot
            capture_output=True,
            text=True,
        ).stdout
    )

    if "error" in file_read.keys():
        if file_read["error"] == 404:
            return HttpResponseNotFound()
        elif file_read["error"] == 500:
            return HttpResponseServerError()

    return FileResponse(
        io.BytesIO(base64.b64decode(file_read[file_to_read]["data"])),
        filename=Path(file_to_read).name,
        content_type=file_read[file_to_read]["mime"],
    )


def get_raw_image(request, image_id) -> HttpResponse:
    """
    Returns the image specified by image_id
    :param request: Django request
    :param image_id: Image ID to request
    :return: FileResponse, or HttpResponse for 403s
    """

    photo = get_object_or_404(Photo, id=image_id)

    if not photo.publicly_accessible:
        # Check if this photo is a part of any publicly visible albums.
        if Album.objects.filter(photos=photo, publicly_accessible=True).count() == 0:
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)

            if photo.user != request.user:
                return HttpResponseForbidden()

    return _get_raw_image(request, photo)


def get_raw_image_album_share(request, image_id, album_share_id) -> HttpResponse:
    """
    Returns the image specified, but authenticated with an album share ID

    :param request: Request object
    :param image_id: ID (UUID) for an image
    :param album_share_id: Album share ID (UUID)
    :return: FileResponse, or HttpResponse for 403s
    """
    photo = get_object_or_404(Photo, id=image_id)
    album_share_link = get_object_or_404(AlbumShareLink, id=album_share_id)

    if photo not in album_share_link.album.photos.all():
        return HttpResponseForbidden()

    return _get_raw_image(request, photo)


def _view_single_photo(
    request, photo: Photo, album_share_id: str = None
) -> HttpResponse:
    """
    Backend method to render single photo page

    :param request: Request object
    :param photo: Photo object
    :param album_share_id: Album share link, if it is to be included
    :return: HttpResponse
    """

    # Find the albums that this photo is a part of
    album_queryset_list = []
    if request.user.is_authenticated:
        album_queryset_list.append(
            Album.objects.filter(photos=photo, owner=request.user)
        )

    if album_share_id:
        album_queryset_list.append(
            Album.objects.filter(
                photos=photo,
                id=get_object_or_404(AlbumShareLink, id=album_share_id).album.id,
            )
        )

    albums = Album.objects.filter(photos=photo, publicly_accessible=True).union(
        *album_queryset_list
    )

    context = {
        "photo": photo,
        "size_hurry": None,
        "album_share_id": album_share_id,
        "license": Photo.License(photo.license).label,
        "albums": albums,
    }

    try:
        context["size_hurry"] = size(photo.image_size)
    except Exception:
        pass

    return render(request, "photos/view_single_photo.html", context=context)


def view_single_photo(request, image_id: str) -> HttpResponse:
    """
    View for a single photo

    :param request: Request object
    :param image_id: ID (UUID) for an image
    :return: HttpResponse
    """
    photo = get_object_or_404(Photo, id=image_id)

    if not photo.publicly_accessible:
        # Check if this photo is a part of any publicly visible albums.
        if Album.objects.filter(photos=photo, publicly_accessible=True).count() == 0:
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)

            if photo.user != request.user:
                return HttpResponseForbidden()

    return _view_single_photo(request, photo)


def view_single_photo_album_share(request, image_id, album_share_id):
    """
    View for a single photo, but authenticated with an album share ID

    :param request: Request object
    :param image_id: ID (UUID) for an image
    :param album_share_id: Album share ID (UUID)
    :return: HttpResponse
    """
    photo = get_object_or_404(Photo, id=image_id)
    album_share_link = get_object_or_404(AlbumShareLink, id=album_share_id)

    if photo not in album_share_link.album.photos.all():
        return HttpResponseForbidden()

    return _view_single_photo(request, photo, album_share_id=album_share_id)


class PhotoUpdate(UserPassesTestMixin, UpdateView):
    model = Photo
    fields = ["description", "license", "publicly_accessible"]
    template_name = "photos/photo_update.html"

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_success_url(self):
        # https://stackoverflow.com/a/64108595/2034128
        pk = self.kwargs["pk"]
        return reverse_lazy("photos:view_single_photo", kwargs={"image_id": pk})


class IndexView(ListView):
    model = Photo
    paginate_by = 100

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Photo.objects.filter(publicly_accessible=True).order_by(
                "-photo_taken_time"
            )
        else:
            return Photo.objects.filter(user=self.request.user).order_by(
                "-photo_taken_time"
            )
