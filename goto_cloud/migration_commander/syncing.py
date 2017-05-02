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
    class SyncingException(Exception):
        """
        raised if an error occurs during the sync
        """
        pass

    def _execute(self):
        self.source_remote_executor = RemoteHostExecutor(self._source.remote_host)
        self._execute_on_every_device(self._sync_disk, self._sync_partition)

        return Commander.Signal.SLEEP

    def _handle_error_report(self, error_report):
        raise SyncCommand.SyncingException(
            'While trying syncing, the following errors occurred. Please resolves these manually '
            'and then skip this step, or retry:\n{errors}'.format(errors=error_report)
        )

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

        try:
            remote_executor.execute(DefaultRemoteHostCommand.MAKE_DIRECTORY.render(directory=temp_mountpoint))
        except RemoteHostExecutor.ExecutionException:
            pass
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
