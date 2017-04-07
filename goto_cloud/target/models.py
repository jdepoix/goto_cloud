from django.db import models
from django.contrib.postgres.fields import JSONField

from remote_host.public import RemoteHost

from tracked_model.public import TrackedModel


class Target(TrackedModel):
    """
    Represents a migration target in the cloud. This is created before the actual migration and used during it, as sort
    of a draft.
    """
    blueprint = JSONField(default=dict)
    remote_host = models.ForeignKey(RemoteHost, related_name='targets', null=True)
