from django.db import models


class BrickModelMixin:
    pass


class BrickModel(BrickModelMixin, models.Model):
    class Meta:
        abstract = True