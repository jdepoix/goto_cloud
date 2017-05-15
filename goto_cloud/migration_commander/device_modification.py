from command.public import SourceCommand

from remote_execution.public import RemoteHostExecutor


class DeviceModifyingCommand(SourceCommand):
    """
    a command supplying utility methods for command which iterate over the devices of the source and target
    """
    def _execute_on_every_device(self, executable_for_disks, executable_for_partitions=None, include_swap=False):
        """
        execute the given executable with all devices.
        
        :param executable_for_disks: a function which takes the parameters: remote_executor, source_device, 
        target_device
        :type executable_for_disks: (self: Any, RemoteExecutor, (str, dict), (str, dict)) -> None
        :param executable: a function which takes the parameters: remote_executor, source_device, 
        target_device, source_partition_device, target_partition_device
        :type executable_for_partitions: (self: Any, RemoteExecutor, (str, dict), (str, dict), (str, dict), (str, dict)
        ) -> None
        :param include_swap: should a swap device also be iterated over
        :type include_swap: bool
        :return: the used remote_executor, for extended use
        :rtype: RemoteHostExecutor
        """
        remote_executor = RemoteHostExecutor(self._target.remote_host)

        for source_device_id, target_device in self._target.device_mapping.items():
            source_device = self._source.remote_host.system_info['block_devices'][source_device_id]

            if executable_for_disks  and (include_swap or not include_swap and source_device['fs'] != 'swap'):
                executable_for_disks(
                    remote_executor,
                    (source_device_id, source_device),
                    (target_device['id'], target_device),
                )

            if executable_for_partitions:
                for source_partition_id, target_partition in target_device['children'].items():
                    source_partition = source_device['children'][source_partition_id]
                    if (include_swap or not include_swap and source_partition['fs'] != 'swap'):
                        executable_for_partitions(
                            remote_executor,
                            (source_device_id, source_device),
                            (target_device['id'], target_device),
                            (
                                source_partition_id,
                                source_partition
                            ),
                            (target_partition['id'], target_partition),
                        )

        return remote_executor

    def _execute_on_every_partition(self, executable):
        """
        executes the given executable on all partitions
        
        :param executable: a function which takes the parameters: remote_executor, source_device, 
        target_device, source_partition_device, target_partition_device
        :type executable: (self: Any, RemoteExecutor, (str, dict), (str, dict), (str, dict), (str, dict)) -> None
        """
        return self._execute_on_every_device(None, executable)
