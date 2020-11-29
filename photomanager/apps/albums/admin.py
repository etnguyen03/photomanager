from django.contrib import admin

from .models import Album, AlbumShareLink


class AlbumAdmin(admin.ModelAdmin):
    readonly_fields = [
        "id",
        "creation_time",
        "last_modified_time",
    ]

    class Meta:
        model = Album


class AlbumShareLinkAdmin(admin.ModelAdmin):
    readonly_fields = [
        "id",
        "creation_time",
    ]

    fields = [
        "id",
        "album",
        "creator",
        "creation_time",
    ]

    # We want the `album` and `creator` attribute to be read-only only when modifying
    # photos, not when creating them.
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(AlbumShareLinkAdmin, self).get_readonly_fields(
            request, obj
        )
        if obj:  # If the object exists; aka we are editing an existing object
            return readonly_fields + ["album", "creator"]
        return readonly_fields

    class Meta:
        model = AlbumShareLink


admin.site.register(Album, AlbumAdmin)
admin.site.register(AlbumShareLink, AlbumShareLinkAdmin)
