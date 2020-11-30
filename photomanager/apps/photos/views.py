import base64
import io
import json
import os
import subprocess
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import FileResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from hurry.filesize import size

from ..albums.models import AlbumShareLink
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
    file_read: dict = json.loads(
        subprocess.run(
            [
                "sudo",
                "pipenv",
                "run",
                "python3",
                READ_FILE_PATH,
                photo.file,
            ],  # sudo required for chroot
            capture_output=True,
            text=True,
        ).stdout
    )

    return FileResponse(
        io.BytesIO(base64.b64decode(file_read[photo.file]["data"])),
        filename=Path(photo.file).name,
        content_type=file_read[photo.file]["mime"],
    )


@login_required
def get_raw_image(request, image_id) -> HttpResponse:
    """
    Returns the image specified by image_id
    :param request: Django request
    :param image_id: Image ID to request
    :return: FileResponse, or HttpResponse for 403s
    """

    photo = get_object_or_404(Photo, id=image_id)

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
    context = {
        "photo": photo,
        "size_hurry": None,
        "album_share_id": album_share_id,
        "license": Photo.License(photo.license).label,
    }

    try:
        context["size_hurry"] = size(photo.image_size)
    except Exception:
        pass

    return render(request, "photos/view_single_photo.html", context=context)


@login_required
def view_single_photo(request, image_id: str) -> HttpResponse:
    """
    View for a single photo

    :param request: Request object
    :param image_id: ID (UUID) for an image
    :return: HttpResponse
    """
    photo = get_object_or_404(Photo, id=image_id)

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
    fields = ["description", "license"]
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
