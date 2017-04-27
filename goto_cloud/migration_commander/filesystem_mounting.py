from .default_remote_host_commands import DefaultRemoteHostCommand
from .device_modification import DeviceModifyingCommand


class FilesystemMountCommand(DeviceModifyingCommand):
    """
    takes care of mounting the filesystems correctly
    """
    class MountingException(Exception):
        """
        raised if an error occurs while mounting
        """
        pass

    def _handle_error_report(self, error_report):
        raise FilesystemMountCommand.MountingException(
            'While trying to mount the filesystems, the following errors occurred. Please resolves these manually '
            'and then skip this step:\n{errors}'.format(errors=error_report)
        )

    def _execute(self):
        self._mount_filesystems()

    def _mount_filesystem_on_disk(self, remote_executor, source_device, target_device):
        """
        creates a filesystem on a disk

        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor 
        :param source_device: the source device
        :type source_device: (str, dict)
        :param target_device: the target device
        :type target_device: (str, dict)
        """
        self._add_mount_to_fstab(
            remote_executor,
            target_device[0],
            target_device[1]['mountpoint'],
            source_device[1]['fs'],
            source_device[1]['uuid'],
            source_device[1]['label'],
        )

    def _mount_filesystem_on_partition(
        self, remote_executor, source_device, target_device, source_partition_device, target_partition_device
    ):
        """
        mounts a filesystem on a partition

        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor 
        :param source_device: the source device
        :type source_device: (str, dict)
        :param target_device: the target device
        :type target_device: (str, dict)
        :param source_partition_device: the original partition device
        :type source_partition_device: (str, dict)
        :param target_partition_device: the target partition device
        :type target_partition_device: (str, dict)
        """
        self._add_mount_to_fstab(
            remote_executor,
            target_partition_device[0],
            target_partition_device[1]['mountpoint'],
            source_partition_device[1]['fs'],
            source_partition_device[1]['uuid'],
            source_partition_device[1]['label'],
        )

    @DeviceModifyingCommand._collect_errors
    def _add_mount_to_fstab(self, remote_executor, device_id, mountpoint, filesystem, uuid=None, label=None):
        """
        adds the mount to /etc/fstab
        
        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor 
        :param device_id: the id of the device which is mounted
        :type: str
        :param mountpoint: the mountpoint
        :type mountpoint: str
        :param filesystem: the filesystem which is mounted on the device
        :type filesystem: str
        :param uuid: optionally the uuid of the device
        :type uuid: str
        :param label: optionally the label of the device
        :type label: str
        """
        if mountpoint:
            remote_executor.execute(DefaultRemoteHostCommand.MAKE_DIRECTORY.render(directory=mountpoint))
            remote_executor.execute(
                DefaultRemoteHostCommand.ADD_FSTAB_ENTRY.render(
                    identifier='UUID={uuid}'.format(uuid=uuid)
                                if uuid else
                                    'LABEL={label}'.format(label=label)
                                    if label else '/dev/{device_id}'.format(device_id=device_id),
                    mountpoint=mountpoint,
                    filesystem=filesystem,
                )
            )

    def _mount_filesystems(self):
        """
        adds the mounts to /etc/fstab and mounts them
        """
        self._reload_mounts(
            self._execute_on_every_device(self._mount_filesystem_on_disk, self._mount_filesystem_on_partition)
        )

    @DeviceModifyingCommand._collect_errors
    def _reload_mounts(self, remote_executor):
        """
        reloads the mounts on the remote host
        
        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor 
        """
        remote_executor.execute(DefaultRemoteHostCommand.RELOAD_MOUNTS.render())
