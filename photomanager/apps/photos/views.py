from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .tasks import scan_dir_for_changes


@login_required
def rescan_directory(request):
    scan_dir_for_changes.delay(request.user.subdirectory, request.user.username)
    return HttpResponse("OK")
