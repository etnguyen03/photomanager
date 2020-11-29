import base64
import io
import json
import os
import subprocess
from fractions import Fraction
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from hurry.filesize import size

from .models import Photo
from .tasks import process_image, scan_dir_for_changes


@login_required
def rescan_directory(request):
    scan_dir_for_changes.delay(request.user.subdirectory, request.user.username)
    return HttpResponse("OK")


@login_required
def reprocess_file(request, image_id):
    try:
        photo = Photo.objects.get(id=image_id)
        if photo.user != request.user:
            return HttpResponseForbidden()
    except Photo.DoesNotExist:
        return Http404()

    process_image.delay(image_id)
    return HttpResponse("OK")


# TODO: Refactor to not require login_required for public viewing
@login_required
def get_raw_image(request, image_id) -> HttpResponse:
    """
    Returns the image specified by image_id
    :param request: Django request
    :param image_id: Image ID to request
    :return: an HTTP response
    """

    photo = get_object_or_404(Photo, id=image_id)

    if photo.user != request.user:
        return HttpResponseForbidden()

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
def view_single_photo(request, image_id):
    photo = get_object_or_404(Photo, id=image_id)

    if photo.user != request.user:
        return HttpResponseForbidden()

    context = {
        "image_id": image_id,
        "photo": photo,
        "size_hurry": None,
        "shutter_speed_seconds": None,
        "aperture_f": None,
    }

    try:
        context["size_hurry"] = size(photo.image_size)
    except Exception:
        pass

    try:
        context["shutter_speed_seconds"] = Fraction(1, 2 ** photo.shutter_speed_value)
    except Exception:
        pass

    return render(request, "photos/view_single_photo.html", context=context)


class PhotoUpdate(UpdateView):
    model = Photo
    fields = ["description"]
    template_name = "photos/photo_update.html"

    def get_success_url(self):
        # https://stackoverflow.com/a/64108595/2034128
        pk = self.kwargs["pk"]
        return reverse_lazy("photos:view_single_photo", kwargs={"image_id": pk})

