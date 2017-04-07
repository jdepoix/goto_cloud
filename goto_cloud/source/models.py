from django.db import models
from django.contrib.postgres.fields.jsonb import JSONField

from migration_run.public import MigrationRun

from remote_host.public import RemoteHost

from target.public import Target

from tracked_model.public import TrackedModel


class Source(TrackedModel):
    """
    represents a source system, which will be migrated to a Target during the migration
    """
    system_info = JSONField(default=dict)
    migration_run = models.ForeignKey(MigrationRun, related_name='sources', null=True,)
    target = models.OneToOneField(Target, related_name='source', null=True,)
    remote_host = models.ForeignKey(RemoteHost, related_name='sources')
