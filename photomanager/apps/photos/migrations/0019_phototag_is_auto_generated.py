# Generated by Django 3.1.4 on 2020-12-04 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("photos", "0018_auto_20201204_2246"),
    ]

    operations = [
        migrations.AddField(
            model_name="phototag",
            name="is_auto_generated",
            field=models.BooleanField(
                default=False,
                help_text="Whether this tag was automatically generated.",
                verbose_name="Automatically generated",
            ),
        ),
    ]
