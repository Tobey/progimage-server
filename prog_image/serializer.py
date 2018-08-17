import base64


from rest_framework import serializers
import magic


from prog_image.models import Image


class Base64ImageField(serializers.ImageField):

    def to_representation(self, image):
        image = image.file.file.read()
        image_type = magic.from_buffer(image, mime=True)
        encoded_image = base64.b64encode(image).decode('utf-8')
        return {'data': encoded_image, 'type': image_type}


class BaseImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = '__all__'


class ImageSerializer(BaseImageSerializer):
    image = Base64ImageField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.is_post:
            data.pop('image')
        return data

    @property
    def is_post(self):
        return self.context['request'].method == 'POST'
