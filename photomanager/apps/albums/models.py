import uuid

from django.db import models

from ..photos.models import Photo
from ..users.models import User


class Album(models.Model):
    """
    Represents an album; a collection of photos.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User, help_text="The user that this album belongs to.", on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=300, help_text="Name for this album.", blank=False, null=False
    )
    description = models.TextField(help_text="Description for this album.", blank=True)

    creation_time = models.DateTimeField(
        auto_now_add=True, help_text="Album creation time.", null=True
    )
    last_modified_time = models.DateTimeField(
        auto_now=True, help_text="Album modification time.", null=True
    )

    publicly_accessible = models.BooleanField(
        default=False,
        null=False,
        help_text="Whether this album is publicly accessible. If checked, this album is "
        "listed on the front page and accessible without authentication. The photos within this album "
        "are not visible on the front page, however, they are publicly accessible with their link.",
    )

    photos = models.ManyToManyField(Photo, blank=True)


class AlbumShareLink(models.Model):
    """
    Represents a share link tied to an album.

    Allows for public viewing of an album and its associated photos with a
    unique link, but without making all the photos in the album public.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    description = models.CharField(max_length=1000, blank=True)

    # Currently, this may seem useless (just read the creator from the album), but
    # in the future when user to user sharing is implemented, this may be useful.
    creator = models.ForeignKey(
        User, help_text="Creator of this Album share link", on_delete=models.CASCADE
    )

    creation_time = models.DateTimeField(
        auto_now_add=True, help_text="Album share link creation time.", null=True
    )
