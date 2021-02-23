import uuid
from fractions import Fraction
from math import sqrt

from django.db import models

from photomanager.apps.faces.models import Face
from photomanager.apps.tags.models import PhotoTag
from photomanager.apps.users.models import User


class Photo(models.Model):
    """
    Represents a single photo.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FilePathField(
        path="/data",
        null=False,
        blank=False,
        help_text="Path to the photo file.",
        allow_files=True,
        allow_folders=False,
        recursive=True,
    )
    user = models.ForeignKey(
        User, help_text="The user that this photo belongs to.", on_delete=models.CASCADE
    )
    description = models.TextField(help_text="Description for this photo.", blank=True)

    class FileTypes(models.IntegerChoices):
        IMAGE = 1
        VIDEO = 2

    file_type = models.IntegerField(choices=FileTypes.choices, null=False, default=1)

    creation_time = models.DateTimeField(
        auto_now_add=True, help_text="Photo creation time.", null=True
    )
    last_modified_time = models.DateTimeField(
        auto_now=True, help_text="Photo modification time.", null=True
    )

    # EXIF Metadata
    photo_taken_time = models.DateTimeField(
        help_text="Time the photo was taken.", null=True, blank=True
    )
    image_height = models.PositiveIntegerField(
        help_text="Height, in pixels, of the image", null=True
    )
    image_width = models.PositiveIntegerField(
        help_text="Width, in pixels, of the image", null=True
    )
    image_size = models.PositiveIntegerField(
        help_text="File size (on disk, in bytes) of the image", null=True
    )

    camera_make = models.CharField(max_length=150, blank=True)
    camera_model = models.CharField(max_length=150, blank=True)

    aperture_value = models.FloatField(
        help_text="Aperture in the APEX system", null=True
    )

    @property
    def aperture_value_f_stop(self) -> float:
        """
        Returns the aperture value as an f-stop.

        :return: a float.
        """
        # Source: http://www.fifi.org/doc/jhead/exif-e.html
        return round(sqrt(2) ** self.aperture_value, 1)

    shutter_speed_value = models.FloatField(
        help_text="Shutter speed in the APEX system", null=True
    )

    @property
    def shutter_speed_seconds(self) -> Fraction:
        """
        Returns the shutter speed value as a fraction of a second.

        :return: a fraction of a second
        """
        return Fraction(1, int(round(2 ** self.shutter_speed_value, 0)))

    focal_length = models.FloatField(help_text="Focal length in millimeters", null=True)
    iso = models.PositiveIntegerField(
        help_text="Sensor sensitivity in ISO", null=True, verbose_name="ISO"
    )

    flash_fired = models.BooleanField(help_text="Did the flash fire?", null=True)

    class FlashMode(models.IntegerChoices):
        """
        Enum for flash_mode field; describes possible flash modes
        """

        UNKNOWN = 0
        COMPULSORY_FLASH_FIRING = 1
        COMPULSORY_FLASH_SUPPRESSION = 2
        AUTOMATIC = 3

    flash_mode = models.IntegerField(
        choices=FlashMode.choices, help_text="Flash firing mode", null=True
    )

    # TODO: GPS information

    # User modifiable metadata
    class License(models.TextChoices):
        """
        Enum of license choices that the user can choose from.
        """

        ARR = ("ARR", "All rights reserved")
        PDM = ("PDM", "Public Domain Mark")
        CC0 = ("CC0", "CC0")
        CCBY = ("CCBY", "Creative Commons Attribution")
        CCBYSA = ("CCBYSA", "Creative Commons Attribution Share-Alike")
        CCBYND = ("CCBYND", "Creative Commons Attribution-NoDerivs")
        CCBYNC = ("CCBYNC", "Creative Commons Attribution-NonCommercial")
        CCBYNCSA = ("CCBYNCSA", "Creative Commons Attribution-NonCommercial-ShareAlike")
        CCBYNCND = ("CCBYNCND", "Creative Commons Attribution-NonCommercial-NoDerivs")

    license = models.CharField(
        max_length=50,
        choices=License.choices,
        default=License.ARR,
        blank=False,
        null=False,
    )

    publicly_accessible = models.BooleanField(
        default=False,
        null=False,
        help_text="Whether this photo is publicly accessible. If checked, this photo is "
        "listed on the front page and accessible without authentication.",
    )

    # Tags; both automatically generated tags and user modifiable
    tags = models.ManyToManyField(PhotoTag, blank=True)

    # Faces; both automatically generated and user modifiable
    faces = models.ManyToManyField(Face, blank=True)
