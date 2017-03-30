from django.db import models

from tracked_model.public import TrackedModel


class RemoteHost(TrackedModel):
    """
    represents an Entity which can be accessed remotely
    """
    address = models.CharField(max_length=512)
    port = models.PositiveIntegerField(default=22)
    username = models.CharField(max_length=512, null=True, blank=True)
    password = models.CharField(max_length=512, null=True, blank=True)
    private_key = models.TextField(null=True, blank=True)
    private_key_file_path = models.CharField(max_length=512, null=True, blank=True)
