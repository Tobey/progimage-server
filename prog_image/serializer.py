from rest_framework import serializers

from prog_image.models import Image


class ImageSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(write_only=True)

    class Meta:
        model = Image
        fields = '__all__'
