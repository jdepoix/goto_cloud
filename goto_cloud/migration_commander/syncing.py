from commander.public import Commander

from remote_execution.public import RemoteHostExecutor

from remote_host_command.public import RemoteHostCommand

from .device_modification import DeviceModifyingCommand
from .default_remote_host_commands import DefaultRemoteHostCommand
from .mountpoint_mapping import MountpointMapper


class SyncCommand(DeviceModifyingCommand):
    """
    does the actual sync and makes sure, that temp mounts are created and used, to avoid problems introduced by 
    overlapping mountpoints.
    """
    class SyncingException(DeviceModifyingCommand.CommandExecutionException):
        """
        raised if an error occurs during the sync
        """
        COMMAND_DOES = 'syncing'

    ERROR_REPORT_EXCEPTION_CLASS = SyncingException

    def _execute(self):
        self.source_remote_executor = RemoteHostExecutor(self._source.remote_host)
        self._execute_on_every_device(self._sync_disk, self._sync_partition)
        self.source_remote_executor.close()
        self.source_remote_executor = None

        return Commander.Signal.SLEEP

    def _sync_disk(self, remote_executor, source_device, target_device):
        self._sync_device(self.source_remote_executor, source_device[1]['mountpoint'], target_device[1]['mountpoint'])

    def _sync_partition(
        self, remote_executor, source_device, target_device, source_partition_device, target_partition_device
    ):
        self._sync_device(
            self.source_remote_executor,
            source_partition_device[1]['mountpoint'],
            target_partition_device[1]['mountpoint'],
        )

    @DeviceModifyingCommand._collect_errors
    def _sync_device(self, remote_executor, source_directory, target_directory):
        if source_directory:
            remote_executor.execute(RemoteHostCommand(self._target.blueprint['commands']['sync']).render(
                source_dir=self._create_temp_bind_mount(remote_executor, source_directory),
                target_dir='{user}{remote_host_address}:{target_directory}'.format(
                    user=('{username}@'.format(username=self._target.remote_host.username))
                            if self._target.remote_host.username else '',
                    remote_host_address=self._target.remote_host.address,
                    target_directory=target_directory,
                )
            ))

    def _create_temp_bind_mount(self, remote_executor, source_directory):
        temp_mountpoint = MountpointMapper.map_mountpoint('/tmp', source_directory)

        remote_executor.execute(
            DefaultRemoteHostCommand.MAKE_DIRECTORY.render(directory=temp_mountpoint)
        )

        try:
            remote_executor.execute(DefaultRemoteHostCommand.CHECK_MOUNTPOINT.render(directory=temp_mountpoint))
        except RemoteHostExecutor.ExecutionException:
            remote_executor.execute(
                DefaultRemoteHostCommand.BIND_MOUNT.render(
                    directory=source_directory,
                    mountpoint=temp_mountpoint
                )
            )

        return temp_mountpoint


class FinalSyncCommand(SyncCommand):
    """
    does a sync like the SyncCommand, but does not return a sleep signal
    """
    def _execute(self):
        super(FinalSyncCommand, self)._execute()
