# Generated by Django 3.1.3 on 2020-11-29 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("albums", "0002_albumsharelink"),
    ]

    operations = [
        migrations.AddField(
            model_name="albumsharelink",
            name="description",
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]