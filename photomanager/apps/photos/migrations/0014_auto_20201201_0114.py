# Generated by Django 3.1.3 on 2020-12-01 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("photos", "0013_photo_publicly_accessible"),
    ]

    operations = [
        migrations.AlterField(
            model_name="photo",
            name="publicly_accessible",
            field=models.BooleanField(
                default=False,
                help_text="Whether this photo is publicly accessible. If checked, this photo is listed on the front page and accessible without authentication.",
            ),
        ),
    ]
