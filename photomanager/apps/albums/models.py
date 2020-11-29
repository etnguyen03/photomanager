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

    photos = models.ManyToManyField(Photo)
