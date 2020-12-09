# Generated by Django 3.1.4 on 2020-12-09 04:57

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("photos", "0001_initial"),
        ("photos", "0002_auto_20201128_2159"),
        ("photos", "0003_auto_20201128_2210"),
        ("photos", "0004_auto_20201128_2211"),
        ("photos", "0005_auto_20201128_2211"),
        ("photos", "0006_auto_20201128_2213"),
        ("photos", "0007_photo_user"),
        ("photos", "0008_auto_20201128_2344"),
        ("photos", "0009_auto_20201128_2351"),
        ("photos", "0010_auto_20201129_0228"),
        ("photos", "0011_auto_20201129_2034"),
        ("photos", "0012_photo_license"),
        ("photos", "0013_photo_publicly_accessible"),
        ("photos", "0014_auto_20201201_0114"),
        ("photos", "0015_auto_20201204_2241"),
        ("photos", "0016_auto_20201204_2244"),
        ("photos", "0017_auto_20201204_2246"),
        ("photos", "0018_auto_20201204_2246"),
        ("photos", "0019_phototag_is_auto_generated"),
        ("photos", "0020_auto_20201209_0438"),
    ]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tags", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PhotoTag",
            fields=[
                ("tag", models.SlugField(primary_key=True, serialize=False)),
                (
                    "create_time",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Creation time"
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "is_auto_generated",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this tag was automatically generated.",
                        verbose_name="Automatically generated",
                    ),
                ),
            ],
        ),
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
                        help_text="Path to the photo file.",
                        path="/data",
                        recursive=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, help_text="Description for this photo."
                    ),
                ),
                (
                    "creation_time",
                    models.DateTimeField(
                        auto_now_add=True, help_text="Photo creation time.", null=True
                    ),
                ),
                (
                    "last_modified_time",
                    models.DateTimeField(
                        auto_now=True, help_text="Photo modification time.", null=True
                    ),
                ),
                (
                    "photo_taken_time",
                    models.DateTimeField(
                        blank=True, help_text="Time the photo was taken.", null=True
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        default=None,
                        help_text="The user that this photo belongs to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.user",
                    ),
                ),
                (
                    "aperture_value",
                    models.FloatField(
                        help_text="Aperture in the APEX system", null=True
                    ),
                ),
                ("camera_make", models.CharField(blank=True, max_length=150)),
                ("camera_model", models.CharField(blank=True, max_length=150)),
                (
                    "flash_fired",
                    models.BooleanField(help_text="Did the flash fire?", null=True),
                ),
                (
                    "flash_mode",
                    models.IntegerField(
                        choices=[
                            (0, "Unknown"),
                            (1, "Compulsory Flash Firing"),
                            (2, "Compulsory Flash Suppression"),
                            (3, "Automatic"),
                        ],
                        help_text="Flash firing mode",
                        null=True,
                    ),
                ),
                (
                    "focal_length",
                    models.FloatField(
                        help_text="Focal length in millimeters", null=True
                    ),
                ),
                (
                    "image_height",
                    models.PositiveIntegerField(
                        help_text="Height, in pixels, of the image", null=True
                    ),
                ),
                (
                    "image_size",
                    models.PositiveIntegerField(
                        help_text="File size (on disk, in bytes) of the image",
                        null=True,
                    ),
                ),
                (
                    "image_width",
                    models.PositiveIntegerField(
                        help_text="Width, in pixels, of the image", null=True
                    ),
                ),
                (
                    "iso",
                    models.PositiveIntegerField(
                        help_text="Sensor sensitivity in ISO",
                        null=True,
                        verbose_name="ISO",
                    ),
                ),
                (
                    "shutter_speed_value",
                    models.FloatField(
                        help_text="Shutter speed in the APEX system", null=True
                    ),
                ),
                (
                    "license",
                    models.CharField(
                        choices=[
                            ("ARR", "All rights reserved"),
                            ("PDM", "Public Domain Mark"),
                            ("CC0", "CC0"),
                            ("CCBY", "Creative Commons Attribution"),
                            ("CCBYSA", "Creative Commons Attribution Share-Alike"),
                            ("CCBYND", "Creative Commons Attribution-NoDerivs"),
                            ("CCBYNC", "Creative Commons Attribution-NonCommercial"),
                            (
                                "CCBYNCSA",
                                "Creative Commons Attribution-NonCommercial-ShareAlike",
                            ),
                            (
                                "CCBYNCND",
                                "Creative Commons Attribution-NonCommercial-NoDerivs",
                            ),
                        ],
                        default="ARR",
                        max_length=50,
                    ),
                ),
                (
                    "publicly_accessible",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this photo is publicly accessible. If checked, this photo is listed on the front page and accessible without authentication.",
                    ),
                ),
                ("tags", models.ManyToManyField(blank=True, to="tags.PhotoTag")),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.AlterModelTable(
                    name="PhotoTag",
                    table="tags_phototag",
                ),
                migrations.AlterField(
                    model_name="photo",
                    name="tags",
                    field=models.ManyToManyField(blank=True, to="tags.PhotoTag"),
                ),
            ],
            state_operations=[
                migrations.DeleteModel(
                    name="PhotoTag",
                ),
            ],
        ),
    ]