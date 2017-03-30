from django.db import models


class TrackedModel(models.Model):
    """
    a model which keeps track of creation and last updated time
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
