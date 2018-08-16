from django.contrib import admin

from prog_image.models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass