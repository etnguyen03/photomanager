# Generated by Django 3.1.4 on 2020-12-04 22:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("photos", "0017_auto_20201204_2246"),
    ]

    operations = [
        migrations.RenameField(
            model_name="phototag",
            old_name="slug",
            new_name="tag",
        ),
    ]