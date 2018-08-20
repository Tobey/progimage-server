import os
import base64
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import CreateModelMixin
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.schemas import AutoSchema
from rest_framework.decorators import action

from PIL import ImageOps
from PIL import Image as image_library

from prog_image.models import Image
from prog_image.serializer import ImageSerializer
from prog_image.serializer import BaseImageSerializer
from prog_image.filters import ImageFilter


MAX_WORKERS = os.getenv('MAX_WORKERS', 5)


class ImageViewSet(RetrieveModelMixin, ListModelMixin, CreateModelMixin, GenericViewSet):

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    list_serializer_class = ImageSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = ImageFilter
    schema = AutoSchema()

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_objects(self):
        return self.filter_queryset(self.get_queryset())

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer(self, *args, **kwargs):
        if not kwargs.get('many'):
            kwargs['many'] = not self.is_retrieve

        return super().get_serializer(*args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        self.reformat_payload(data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['GET'], detail=False)
    def png(self, request):
        image_format = 'PNG'
        return self.image_format(image_format=image_format)

    @action(methods=['GET'], detail=False)
    def jpeg(self, request):
        image_format = 'JPEG'
        return self.image_format(image_format=image_format)

    @action(methods=['GET'], detail=False)
    def tiff(self, request):
        image_format = 'TIFF'
        return self.image_format(image_format=image_format)

    @action(methods=['GET'], detail=False)
    def giff(self, request):
        image_format = 'GIF'
        return self.image_format(image_format=image_format)

    @action(methods=['GET'], detail=False)
    def invert(self, request):
        return self.image_rotate(direction=image_library.FLIP_TOP_BOTTOM)

    @action(methods=['GET'], detail=False)
    def rotate(self, request):
        return self.image_rotate(direction=image_library.ROTATE_90)

    @action(methods=['GET'], detail=False)
    def thumbnail(self, request):
        size = (36, 36)
        image_format = 'JPEG'
        queryset = self.paginate_queryset(self.get_objects())
        with ThreadPoolExecutor(max_workers=10) as executor:
            processed_images = [
                executor.submit(self._thumbnail, instance, image_format, size).result() for instance in queryset
            ]
        return self.get_response(processed_images)

    @action(methods=['GET'], detail=False)
    def url(self, request):
        queryset = self.paginate_queryset(self.get_objects())
        serializer = BaseImageSerializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def image_rotate(self, *, direction):
        queryset = self.paginate_queryset(self.get_objects())
        with ThreadPoolExecutor(max_workers=10) as executor:
            processed_images = [
                executor.submit(self._rotate, instance, direction=direction).result() for instance in queryset
            ]
        return self.get_response(processed_images)

    def image_format(self, *, image_format):
        queryset = self.paginate_queryset(self.get_objects())
        with ThreadPoolExecutor(max_workers=10) as executor:
            processed_images = [
                executor.submit(self._convert, instance, image_format).result() for instance in queryset
            ]
        return self.get_response(processed_images)

    @staticmethod
    def _convert(image_obj, image_format):
        image = image_library.open(image_obj.image.file).convert('RGB')
        output = BytesIO()
        image.save(output, format=image_format)
        image_data = base64.b64encode(output.getvalue()).decode('utf-8')
        return dict(image_data=image_data, image_id=image_obj.id, image_format=image_format)

    @staticmethod
    def _rotate(image_obj, direction=None):
        image = image_library.open(image_obj.image.file)
        new_image = image.transpose(direction)
        output = BytesIO()
        new_image.save(output)
        image_data = base64.b64encode(output.getvalue()).decode('utf-8')
        return dict(image_data=image_data, image_id=image_obj.id, image_format=image.format)

    @staticmethod
    def _thumbnail(image_obj, image_format, size):
        image = image_library.open(image_obj.image.file).convert('RGB')
        thumbnail = ImageOps.fit(image, size, image_library.ANTIALIAS)
        output = BytesIO()
        thumbnail.save(output, format=image_format)
        thumbnail_data = base64.b64encode(output.getvalue()).decode('utf-8')
        return dict(image_data=thumbnail_data, image_id=image_obj.id, image_format=image_format)

    def reformat_payload(self, data):
        """Reformat for bulk upload in html format [0]image, [1]image, ..."""

        fields_to_format = ('image', 'image_url')
        for field in fields_to_format:
            images = data.getlist(field, [])
            for idx, im in enumerate(images):
                data[f'[{idx}]{field}'] = im

    def get_response(self, processed_images):
        response = []
        for image in processed_images:
            response.append(dict(
                id=image['image_id'], image=dict(
                    format=image['image_format'], data=image['image_data'])
            ))
        return self.get_paginated_response(response)

    @property
    def is_retrieve(self):
        return self.request.method == 'GET' and self.request.parser_context['kwargs'].get('pk')
