import base64
from io import BytesIO

import magic
import requests

from django.contrib.auth.models import User
from django.forms import URLField
from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework import serializers

from prog_image.models import Image


VALID_IMAGE_EXTENSIONS = [
    'jpg',
    'jpeg',
    'png',
    'gif',
]

url_field = URLField()


def image_url_validator(url):
    url = url_field.clean(url)
    ext = url.rsplit('.', 1)[-1]
    assert ext in VALID_IMAGE_EXTENSIONS, f'use valid image urls with extention {VALID_IMAGE_EXTENSIONS}'
    return url


class Base64ImageField(serializers.ImageField):

    def to_representation(self, image):
        image = image.file.read()
        image_type = magic.from_buffer(image, mime=True)
        encoded_image = base64.b64encode(image).decode('utf-8')
        return {'data': encoded_image, 'type': image_type}


class BaseImageSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all())
    image_url = serializers.URLField(validators=[image_url_validator], required=False)

    def to_internal_value(self, data):
        data = data.copy()
        data['user'] = self.context['request'].user.id
        return super().to_internal_value(data)

    class Meta:
        model = Image
        fields = ('id', 'image', 'user', 'image_url')


class ImageSerializer(BaseImageSerializer):
    image = Base64ImageField(required=True)

    def download_image(self, url):
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        file = BytesIO()
        file.write(response.content)
        file.seek(0)
        ext = url.rsplit('.', 1)[-1]
        image_as_file = InMemoryUploadedFile(
            file=file, field_name='image', name=f'uploaded.{ext}',
            content_type='image/{ext}', size=len(response.content), charset=None
        )
        return image_as_file

    def to_internal_value(self, data):
        data = data.copy()
        url = data.pop('image_url', None)
        if url:
            data['image'] = self.download_image(url[0])
        return super().to_internal_value(data)
