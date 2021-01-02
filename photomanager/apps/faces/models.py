import uuid

from django.db import models

from photomanager.apps.users.models import User


class Face(models.Model):
    """
    Represents a face in an image.

    These faces can be tied to a User or they can not be.
    """

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    defined_name = models.CharField(
        max_length=250,
        help_text="Name for this face. Ignored if a user is defined",
        blank=True,
    )

    # We use a ForeignKey because it might be possible that multiple "faces" are detected
    # but all of those "faces" correspond to the same person
    user = models.ForeignKey(
        User,
        models.SET_NULL,
        null=True,
        blank=True,
        help_text="The user that whose face is represented by this object.",
    )

    creator = models.ForeignKey(
        User,
        models.SET_NULL,
        null=True,
        blank=True,
        help_text="The user that created this object.",
        related_name="creator",
    )
    modify_time = models.DateTimeField(verbose_name="Last modified time", auto_now=True)
    create_time = models.DateTimeField(verbose_name="Creation time", auto_now_add=True)

    face_data = models.TextField(
        help_text="Internal data used to recognize this face.", max_length=5000
    )

    @property
    def name(self):
        if self.user is User:  # i.e. not None
            if self.user.get_full_name().strip() != "":
                return self.user.get_full_name().strip()
        return self.defined_name

    def __str__(self):
        return f"{self.name} ({self.id})"
