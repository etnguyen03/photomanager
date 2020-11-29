from django.contrib import admin

from .models import Album


class AlbumAdmin(admin.ModelAdmin):
    readonly_fields = [
        "id",
        "creation_time",
        "last_modified_time",
    ]

    class Meta:
        model = Album


admin.site.register(Album, AlbumAdmin)
