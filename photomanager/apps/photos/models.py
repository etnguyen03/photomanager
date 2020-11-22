from django.db import models

import uuid


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
        editable=False,
    )
    description = models.TextField(help_text="Description for this photo.")

    creation_time = models.DateTimeField(
        auto_now_add=True, help_text="Photo creation time."
    )
    last_modified_time = models.DateTimeField(
        auto_now=True, help_text="Photo modification time."
    )
    photo_taken_time = models.DateTimeField(help_text="Time the photo was taken.")
