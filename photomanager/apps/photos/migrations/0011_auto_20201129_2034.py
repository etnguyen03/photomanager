# Generated by Django 3.1.3 on 2020-11-29 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("photos", "0010_auto_20201129_0228"),
    ]

    operations = [
        migrations.AlterField(
            model_name="photo",
            name="description",
            field=models.TextField(blank=True, help_text="Description for this photo."),
        ),
    ]
