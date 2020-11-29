from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render

from photomanager.apps.albums.models import Album


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
