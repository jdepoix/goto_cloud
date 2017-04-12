from django.db import models
from django.contrib.postgres.fields.jsonb import JSONField

from enums.public import StringEnum

from migration_run.public import MigrationRun

from remote_host.public import RemoteHost

from target.public import Target

from status_model.public import StatusModel


class Source(StatusModel):
    """
    represents a source system, which will be migrated to a Target during the migration
    """
    class Status(StringEnum):
        DRAFT = 'DRAFT'
        SYNCING = 'SYNCING'
        LIVE = 'LIVE'

    _LIFECYCLE = (
        Status.DRAFT,
        Status.SYNCING,
        Status.LIVE,
    )

    @property
    def lifecycle(self):
        return self._LIFECYCLE

    system_info = JSONField(default=dict)
    migration_run = models.ForeignKey(MigrationRun, related_name='sources', null=True,)
    target = models.OneToOneField(Target, related_name='source', null=True,)
    remote_host = models.ForeignKey(RemoteHost, related_name='sources')
