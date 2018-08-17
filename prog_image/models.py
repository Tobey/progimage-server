import uuid

from django.db import models


class Image(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    image = models.ImageField(upload_to='')
