import base64
import io
import json
import multiprocessing
import os
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import billiard
import magic
import pytz
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from exif import Image as exif_Image
from PIL import Image as PIL_Image
from PIL import ImageOps
from timezonefinder import TimezoneFinder

if settings.ENABLE_TENSORFLOW_TAGGING:
    import numpy as np
    from tensorflow.keras.applications import NASNetLarge
    from tensorflow.keras.applications.imagenet_utils import (
        decode_predictions,
        preprocess_input,
    )
    from tensorflow.keras.preprocessing import image as keras_image

from ..tags.models import PhotoTag
from .models import Photo

LOCK_EXPIRE = 60 * 10


@contextmanager
def redis_lock(lock_id):
    """
    Helper function to manage locks in the Redis database
    From https://docs.celeryproject.org/en/latest/tutorials/task-cookbook.html

    :param lock_id: An ID for the lock
    """
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    # Second value is arbitrary
    status = cache.add(lock_id, "lock", timeout=LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


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

    if contents.returncode != 0:
        raise Exception()

    user = get_user_model().objects.get(username=username)

    for file, mime in json.loads(contents.stdout).items():
        if "image" in mime:
            # file must be prepended with user.subdirectory
            actual_path = os.path.join("/data/", str(user.subdirectory), file)
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
    # TODO: find a better way to do this
    file_path = "/data/" + str(photo.file).lstrip("/")
    file_read: dict = json.loads(
        subprocess.run(
            [
                "sudo",
                "pipenv",
                "run",
                "python3",
                READ_FILE_PATH,
                file_path,
            ],  # sudo required for chroot
            capture_output=True,
            text=True,
        ).stdout
    )

    if "error" in file_read.keys():
        if file_read["error"] == 404:
            raise Exception()
        elif file_read["error"] == 500:
            raise Exception()

    assert "image" in file_read[file_path]["mime"], "Not an image"

    image_data: bytes = base64.b64decode(file_read[file_path]["data"])

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
            gps_point = []
            for pt, direction in [
                (exif_image.gps_latitude, exif_image.gps_latitude_ref),
                (exif_image.gps_longitude, exif_image.gps_longitude_ref),
            ]:
                deg, minutes, seconds = pt
                # https://stackoverflow.com/a/54294962
                point = (
                    float(deg) + float(minutes) / 60 + float(seconds) / (60 * 60)
                ) * (-1 if direction in ["W", "S"] else 1)
                gps_point.append(point)
            tz = tf.timezone_at(lat=gps_point[0], lng=gps_point[1])
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
    photo.image_size = file_read[file_path]["size"]

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

    if settings.ENABLE_TENSORFLOW_TAGGING:
        # We only want to run one tagging operation at a time since it is memory intensive
        with redis_lock("tensorflow-tag"):
            # We define get_predictions to allow for a timeout
            # The queue is created to grab the return value
            queue = multiprocessing.Queue()

            def get_predictions(img_pillow: PIL_Image):
                """
                Helper function to determine tags of an image
                :param img_pillow: Pillow.Image
                :return: None (results appended to queue)
                """
                model = NASNetLarge(weights="imagenet")
                image_tags = keras_image.img_to_array(
                    img_pillow.resize((331, 331), PIL_Image.NEAREST)
                )
                image_tags = np.expand_dims(image_tags, axis=0)
                image_tags = preprocess_input(image_tags)
                predictions = model.predict(image_tags)
                queue.put(decode_predictions(predictions)[0])

            process = billiard.context.Process(
                target=get_predictions, kwargs={"img_pillow": image_pillow}
            )
            process.daemon = True
            process.start()

            process.join(60)  # 60 second (arbitrary) timeout
            if process.is_alive():
                process.terminate()
                raise TimeoutError

            decoded_predictions = queue.get()

            for prediction in decoded_predictions:
                if (
                    prediction[2] > 0.20
                ):  # If score greater than 0.20 (chosen arbitrarily)
                    tag = PhotoTag.objects.get_or_create(tag=prediction[1])
                    if tag[1]:  # If an object was created
                        tag[0].is_auto_generated = True
                        tag[0].save()
                    photo.tags.add(tag[0])

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
