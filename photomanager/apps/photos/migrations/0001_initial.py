# Generated by Django 3.1.3 on 2020-11-22 03:38

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Photo",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "file",
                    models.FilePathField(
                        editable=False,
                        help_text="Path to the photo file.",
                        path="/data",
                    ),
                ),
                (
                    "description",
                    models.TextField(help_text="Description for this photo."),
                ),
                (
                    "creation_time",
                    models.DateTimeField(
                        auto_now_add=True, help_text="Photo creation time."
                    ),
                ),
                (
                    "last_modified_time",
                    models.DateTimeField(
                        auto_now=True, help_text="Photo modification time."
                    ),
                ),
                (
                    "photo_taken_time",
                    models.DateTimeField(help_text="Time the photo was taken."),
                ),
            ],
        ),
    ]
