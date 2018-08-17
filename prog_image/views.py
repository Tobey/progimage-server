import base64
from io import BytesIO

from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.schemas import AutoSchema

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import CreateModelMixin

from rest_framework.decorators import action


from PIL import ImageOps
from PIL import Image as image_library

from prog_image.models import Image
from prog_image.serializer import ImageSerializer
from prog_image.serializer import BaseImageSerializer
from prog_image.filters import ImageFilter


class ImageViewSet(RetrieveModelMixin, ListModelMixin, CreateModelMixin, GenericViewSet):

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    filter_class = ImageFilter
    schema = AutoSchema()

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['many'] = True
        return context

    @action(methods=['GET'], detail=True)
    def png(self, request, pk):
        image_format = 'PNG'
        instance = self.get_object()
        image_data = self.convert(instance, image_format)
        return self.get_response(image_id=instance.id, image_data=image_data, image_type=image_format)

    @action(methods=['GET'], detail=True)
    def jpeg(self, request, pk):
        image_format = 'JPEG'
        instance = self.get_object()
        image_data = self.convert(instance, image_format)
        return self.get_response(image_id=instance.id, image_data=image_data, image_type=image_format)

    @action(methods=['GET'], detail=True)
    def tiff(self, request, pk):
        image_format = 'TIFF'
        instance = self.get_object()
        image_data = self.convert(instance, image_format)
        return self.get_response(image_id=instance.id, image_data=image_data, image_type=image_format)

    @action(methods=['GET'], detail=True)
    def gif(self, request, pk):
        image_format = 'GIF'
        instance = self.get_object()
        image_data = self.convert(instance, image_format)
        return self.get_response(image_id=instance.id, image_data=image_data, image_type=image_format)

    @action(methods=['GET'], detail=True)
    def invert(self, request, pk):
        instance = self.get_object()
        image_data, image_format= self.rotate(instance, direction=image_library.FLIP_TOP_BOTTOM)
        return self.get_response(image_id=instance.id, image_data=image_data, image_type=image_format)

    @action(methods=['GET'], detail=True)
    def rotate(self, request, pk):
        instance = self.get_object()
        image_data, image_format= self.rotate(instance, direction=image_library.ROTATE_90)
        return self.get_response(image_id=instance.id, image_data=image_data, image_type=image_format)

    @action(methods=['GET'], detail=True)
    def thumbnail(self, request, pk):
        size = (36, 36)
        image_format = 'JPEG'
        instance = self.get_object()
        image = image_library.open(instance.image.file).convert('RGB')
        thumbnail = ImageOps.fit(image, size, image_library.ANTIALIAS)
        output = BytesIO()
        thumbnail.save(output, format=image_format)
        thumbnail_data = base64.b64encode(output.getvalue()).decode('utf-8')
        return self.get_response(image_id=instance.id, image_data=thumbnail_data, image_type=image_format)

    @action(methods=['GET'], detail=True)
    def url(self, request, pk):
        instance = self.get_object()
        return JsonResponse(BaseImageSerializer(instance).data)

    @staticmethod
    def convert(image_obj, image_format):
        image = image_library.open(image_obj.image.file).convert('RGB')
        output = BytesIO()
        image.save(output, format=image_format)
        image_data = base64.b64encode(output.getvalue()).decode('utf-8')
        return image_data

    @staticmethod
    def rotate(image_obj, direction=None):
        image = image_library.open(image_obj.image.file)
        new_image = image.transpose(direction)
        output = BytesIO()
        new_image.save(output)
        image_data = base64.b64encode(output.getvalue()).decode('utf-8')
        return image_data, new_image.format

    @staticmethod
    def get_response(*, image_id, image_data, image_type):
        return JsonResponse(dict(id=image_id, image=dict(type=f'image/{image_type.lower()}', data=image_data)))

