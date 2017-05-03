from django.db import models

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
        GET_TARGET_SYSTEM_INFORMATION = 'GET_TARGET_SYSTEM_INFORMATION'
        IDENTIFY_DEVICES = 'IDENTIFY_DEVICES'
        CREATE_PARTITIONS = 'CREATE_PARTITIONS'
        CREATE_FILESYSTEMS = 'CREATE_FILESYSTEMS'
        MOUNT_FILESYSTEMS = 'MOUNT_FILESYSTEMS'
        SYNCING = 'SYNCING'
        FINAL_SYNC = 'FINAL_SYNC'
        ADJUST_NETWORK_CONFIG = 'ADJUST_NETWORK_CONFIG'
        ADJUST_SSH_CONFIG = 'ADJUST_SSH_CONFIG'
        ADJUST_FSTAB = 'ADJUST_FSTAB'
        REINSTALL_BOOTLOADER = 'REINSTALL_BOOTLOADER'
        LIVE = 'LIVE'

    _LIFECYCLE = (
        Status.DRAFT,
        Status.GET_TARGET_SYSTEM_INFORMATION,
        Status.IDENTIFY_DEVICES,
        Status.CREATE_PARTITIONS,
        Status.CREATE_FILESYSTEMS,
        Status.MOUNT_FILESYSTEMS,
        Status.SYNCING,
        Status.FINAL_SYNC,
        Status.ADJUST_NETWORK_CONFIG,
        Status.ADJUST_SSH_CONFIG,
        Status.ADJUST_FSTAB,
        Status.REINSTALL_BOOTLOADER,
        Status.LIVE,
    )

    @property
    def lifecycle(self):
        return self._LIFECYCLE

    migration_run = models.ForeignKey(MigrationRun, related_name='sources', null=True,)
    target = models.OneToOneField(Target, related_name='source', null=True,)
    remote_host = models.ForeignKey(RemoteHost, related_name='sources')
