from django.db import models

from photomanager.apps.users.models import User


class PhotoTag(models.Model):
    tag = models.SlugField(primary_key=True)

    @property
    def human_readable_name(self) -> str:
        """
        Return a human readable name based off the slug.
        :return: A string
        """
        return self.tag.replace("_", " ")

    is_auto_generated = models.BooleanField(
        verbose_name="Automatically generated",
        default=False,
        help_text="Whether this tag was automatically generated.",
    )

    creator = models.ForeignKey(User, models.SET_NULL, null=True)
    create_time = models.DateTimeField(verbose_name="Creation time", auto_now_add=True)

    def __str__(self):
        return self.human_readable_name
