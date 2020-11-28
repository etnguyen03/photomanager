from django.contrib.auth.models import AbstractUser
from django.db.models.fields import FilePathField


class User(AbstractUser):
    """
    User object.
    """

    # Subdirectory under their `data` folder where photos belong.
    # We assume that the `data` folder is bind-mounted in using Docker
    # (or, in a development environment, just exists) at `/data`.
    # Each user has a folder in `/data`.
    subdirectory = FilePathField(
        path="/data",
        null=False,
        blank=False,
        default="/data/",
        recursive=True,
        allow_folders=True,
        allow_files=False,
    )
