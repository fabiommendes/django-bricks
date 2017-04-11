from django.db import models


class RenderableModel(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return 'obj'

    def get_absolute_url(self):
        return 'absolute-url'