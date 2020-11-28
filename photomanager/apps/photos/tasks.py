import base64
import json
import os
import subprocess
from pathlib import Path

from celery import shared_task
from django.contrib.auth import get_user_model
from exif import Image

from .models import Photo


@shared_task
def scan_dir_for_changes(directory: Path, username: str) -> None:
    """
    Scans the directory given for new files.
    Queues new tasks for any new files found.

    :param directory: The directory to scan.
    :param username: Username that this directory corresponds to
    :return: None
    """

    LIST_DIR_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "utils/files/list_dir.py",
    )

    # First, list the directory
    # sudo required for chroot
    contents = subprocess.run(
        ["sudo", "pipenv", "run", "python3", LIST_DIR_PATH, str(directory)],
        capture_output=True,
        text=True,
    )

    user = get_user_model().objects.get(username=username)

    for file, mime in json.loads(contents.stdout).items():
        # file[0] is the file name, file[1] is the mime type
        if "image" in mime:
            # file must be prepended with user.subdirectory
            actual_path = f"{str(user.subdirectory)}{file}"
            photo = Photo.objects.get_or_create(file=actual_path, user=user)
            if photo[1]:  # If this was just created by get_or_create
                process_image.delay(photo.id)


@shared_task
def process_image(photo_id: str) -> None:
    """
    Process an image.

    :param photo_id: The UUID of a photo
    :return: None
    """
    photo = Photo.objects.get(id=photo_id)

    # Read this file
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

    assert "image" in file_read[photo.file]["mime"], "Not an image"

    image_data: bytes = base64.b64decode(file_read[photo.file]["data"])

    exif_image = Image(image_data)
