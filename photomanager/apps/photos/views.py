from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseForbidden

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
