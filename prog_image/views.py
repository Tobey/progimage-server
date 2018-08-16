from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import CreateModelMixin

from prog_image.models import Image
from prog_image.serializer import ImageSerializer


class ImageViewSet(RetrieveModelMixin, CreateModelMixin, GenericViewSet):

    queryset = Image.objects.all()
    serializer_class = ImageSerializer


