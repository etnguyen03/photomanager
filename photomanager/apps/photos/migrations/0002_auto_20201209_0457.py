# Generated by Django 3.1.4 on 2020-12-09 04:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("photos", "0001_squashed_0020_auto_20201209_0438"),
    ]

    operations = [
        migrations.AlterField(
            model_name="photo",
            name="user",
            field=models.ForeignKey(
                help_text="The user that this photo belongs to.",
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
