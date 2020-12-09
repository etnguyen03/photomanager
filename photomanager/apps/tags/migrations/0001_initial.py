# Generated by Django 3.1.4 on 2020-12-09 04:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    state_operations = [
        migrations.CreateModel(
            name="PhotoTag",
            fields=[
                ("tag", models.SlugField(primary_key=True, serialize=False)),
                (
                    "is_auto_generated",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this tag was automatically generated.",
                        verbose_name="Automatically generated",
                    ),
                ),
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
            ],
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
