import uuid

from django.db import models
from django.contrib.auth.models import User


class Image(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    image = models.ImageField(upload_to='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
