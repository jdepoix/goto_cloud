from remote_host_command.public import RemoteHostCommand

from .device_modification import DeviceModifyingCommand


class CreateFilesystemsCommand(DeviceModifyingCommand):
    """
    takes care, of creating the filesystems
    """
    class UnsupportedFilesystemException(Exception):
        """
        raised if a filesystem is not supported
        """
        pass

    def _execute(self):
        errors = self._execute_on_every_device(self._create_filesystem_on_disk, self._create_filesystem_on_partition)

        if errors:
            raise CreateFilesystemsCommand.UnsupportedFilesystemException(
                'While trying to create the partitions, the following errors occurred. Please resolves these manually '
                'and then skip this step:\n{errors}'.format(
                    errors='\n\n-------------------------------------------------------------\n'.join(errors)
                )
            )

    def _create_filesystem_on_partition(self, remote_executor, source_device, target_device, partition_device):
        """
        creates a filesystem on a partition
        
        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor 
        :param source_device: the source device
        :type source_device: (str, dict)
        :param target_device: the target device
        :type target_device_id: (str, dict)
        :param partition_device: the original partition device
        :type partition_device: (str, dict)
        :return: a error which occurred during execution (in case it did...)
        :rtype: str
        """
        return self._create_filesystem(remote_executor, partition_device, target_device[0] + partition_device[0][-1])

    def _create_filesystem_on_disk(self, remote_executor, source_device, target_device):
        """
        creates a filesystem on a disk

        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor 
        :param source_device: the source device
        :type source_device: (str, dict)
        :param target_device: the target device
        :type target_device: (str, dict)
        :return: a error which occurred during execution (in case it did...)
        :rtype: str
        """
        return self._create_filesystem(remote_executor, source_device, target_device[0])

    def _create_filesystem(self, remote_executor, source_device, target_device_id):
        """
        creates a filesystem independent of the device type

        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor 
        :param source_device: the source device
        :type source_device: (str, dict)
        :param target_device: the target device id
        :type target_device: str
        :return: a error which occurred during execution (in case it did...)
        :rtype: str
        """
        if source_device[1]['fs']:
            if source_device[1]['fs'] in self._target.blueprint['commands']['create_filesystem']:
                return self._execute_and_return_errors(
                    lambda: remote_executor.execute(
                        RemoteHostCommand(
                            self._target.blueprint['commands']['create_filesystem'][source_device[1]['fs']]
                        ).render(
                            device='/dev/{device_id}'.format(device_id=target_device_id),
                            **{'uuid': source_device[1]['uuid']} if source_device[1]['uuid'] else {},
                            **{'label': source_device[1]['label']} if source_device[1]['label'] else {},
                        )
                    )
                )
            else:
                return (
                    'The device {source_device_id} can not be replicated, since the filesystem {filesystem} is not '
                    'supported!'.format(
                        source_device_id=source_device[0],
                        filesystem=source_device[1]['fs']
                    )
                )

        return None
