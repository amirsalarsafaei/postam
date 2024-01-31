import uuid

from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField


class UserPost(models.Model):
    user = models.ForeignKey(to=User, to_field='id', on_delete=models.CASCADE)

    token = models.CharField(max_length=15, unique=True)
    title = models.CharField(max_length=512)
    images = ArrayField(
        models.URLField(),
    )
    category = models.CharField(max_length=64)


class Vitrine(models.Model):
    slug = models.UUIDField(unique=True, default=uuid.uuid4)
    posts = models.ManyToManyField(to=UserPost)

