import base64
import io
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import magic
import pytz
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from exif import Image as exif_Image
from PIL import Image as PIL_Image
from PIL import ImageOps
from timezonefinder import TimezoneFinder

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
                process_image.delay(photo[0].id)


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

    m = magic.Magic(mime=True)
    assert "image" in m.from_buffer(image_data), "Not an image file"

    exif_image = exif_Image(image_data)

    # Update the photo's metadata

    if "datetime" in dir(exif_image):
        # EXIF does not include timezones (WHY?!?) in timestamps.
        # Therefore, we use the GPS location to find the timezone of the image,
        # and where there is no GPS location, we use server time (likely UTC).
        tf = TimezoneFinder()

        if "gps_longitude" in dir(exif_image) and "gps_latitude" in dir(exif_image):
            deg, minutes, seconds = exif_image.gps_longitude
            direction = exif_image.gps_longitude_ref
            # https://stackoverflow.com/a/54294962
            longitude = (
                float(deg) + float(minutes) / 60 + float(seconds) / (60 * 60)
            ) * (-1 if direction in ["W", "S"] else 1)

            deg, minutes, seconds = exif_image.gps_latitude
            direction = exif_image.gps_latitude_ref
            latitude = (
                float(deg) + float(minutes) / 60 + float(seconds) / (60 * 60)
            ) * (-1 if direction in ["W", "S"] else 1)
            tz = tf.timezone_at(lng=longitude, lat=latitude)
        else:
            tz = settings.TIME_ZONE

        photo.photo_taken_time = datetime.strptime(
            exif_image.datetime, "%Y:%m:%d %H:%M:%S"
        ).replace(tzinfo=pytz.timezone(tz))

    # Height and width are a property of every image
    image_pillow = PIL_Image.open(io.BytesIO(image_data))
    image_pillow = ImageOps.exif_transpose(image_pillow)
    width, height = image_pillow.size
    photo.image_width = width
    photo.image_height = height
    photo.image_size = file_read[photo.file]["size"]

    if "make" in dir(exif_image):
        photo.camera_make = exif_image.make
    if "model" in dir(exif_image):
        photo.camera_model = exif_image.model
    if "aperture_value" in dir(exif_image):
        photo.aperture_value = exif_image.aperture_value
    if "shutter_speed_value" in dir(exif_image):
        photo.shutter_speed_value = exif_image.shutter_speed_value
    if "focal_length" in dir(exif_image):
        photo.focal_length = exif_image.focal_length
    if "photographic_sensitivity" in dir(exif_image):
        photo.iso = exif_image.photographic_sensitivity
    if "flash" in dir(exif_image):
        photo.flash_fired = exif_image.flash.flash_fired
        photo.flash_mode = exif_image.flash.flash_mode

    # We will need to make a thumbnail of this image
    image_pillow.thumbnail((1024, 1024))

    # Save the thumbnail in a directory
    # This directory is under settings.IMAGE_THUMBS_DIR, and
    # we use the first two characters of the photo's UUID as subdirectories
    # to save images under

    path = os.path.join(settings.IMAGE_THUMBS_DIR, photo_id[0], photo_id[1])
    Path(os.path.join(settings.IMAGE_THUMBS_DIR, photo_id[0], photo_id[1])).mkdir(
        parents=True, exist_ok=True
    )

    image_pillow.save(os.path.join(path, f"{photo_id}.thumb.jpeg"))

    photo.save()
