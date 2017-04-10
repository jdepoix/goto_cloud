from django.db import models

from operating_system.public import OperatingSystem

from tracked_model.public import TrackedModel


class RemoteHost(TrackedModel):
    """
    represents an Entity which can be accessed remotely
    """
    # os default is Debian, as of now, since only Linux is supported. Should be changed, if support for others is added.
    os = models.CharField(max_length=255, default=OperatingSystem.DEBIAN, choices=OperatingSystem.get_django_choices())
    version = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=512)
    port = models.PositiveIntegerField(default=22)
    username = models.CharField(max_length=512, null=True, blank=True)
    password = models.CharField(max_length=512, null=True, blank=True)
    private_key = models.TextField(null=True, blank=True)
    private_key_file_path = models.CharField(max_length=512, null=True, blank=True)
