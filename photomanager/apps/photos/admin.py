from django.contrib import admin

from .models import Photo


class PhotoAdmin(admin.ModelAdmin):
    readonly_fields = [
        "creation_time",
        "last_modified_time",
        "id",
        "photo_taken_time",
        "image_height",
        "image_width",
        "image_size",
        "camera_make",
        "camera_model",
        "aperture_value",
        "shutter_speed_value",
        "focal_length",
        "iso",
        "flash_fired",
        "flash_mode",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "file",
                    "user",
                    "description",
                    "license",
                    "creation_time",
                    "last_modified_time",
                )
            },
        ),
        (
            "Image EXIF data",
            {
                "fields": (
                    "photo_taken_time",
                    "image_height",
                    "image_width",
                    "image_size",
                    "camera_make",
                    "camera_model",
                    "aperture_value",
                    "shutter_speed_value",
                    "focal_length",
                    "iso",
                    "flash_fired",
                    "flash_mode",
                )
            },
        ),
    )

    # We want the `file` attribute to be read-only only when modifying
    # photos, not when creating them.
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(PhotoAdmin, self).get_readonly_fields(request, obj)
        if obj:  # If the object exists; aka we are editing an existing object
            return readonly_fields + ["file"]
        return readonly_fields

    class Meta:
        model = Photo


admin.site.register(Photo, PhotoAdmin)
