# Generated by Django 3.1.4 on 2020-12-03 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("photos", "0014_auto_20201201_0114"),
        ("albums", "0006_auto_20201202_1956"),
    ]

    operations = [
        migrations.AlterField(
            model_name="album",
            name="photos",
            field=models.ManyToManyField(blank=True, to="photos.Photo"),
        ),
    ]