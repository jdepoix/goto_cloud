from command.public import SourceCommand

from remote_execution.public import RemoteHostExecutor


class DeviceModifyingCommand(SourceCommand):
    """
    a command supplying utility methods for command which iterate over the devices of the source and target
    """
    def _execute_on_every_device(self, executable_for_disks, executable_for_partitions):
        """
        execute the given executable with all devices.
        
        :param executable_for_disks: a function which takes the parameters: remote_executor, source_device, 
        target_device
        :type executable_for_disks: (self: Any, RemoteExecutor, (str, dict), (str, dict)) -> None
        :param executable: a function which takes the parameters: remote_executor, source_device, 
        target_device, partition_device
        :type executable_for_partitions: (self: Any, RemoteExecutor, (str, dict), (str, dict), (str, dict)) -> None
        """
        remote_executor = RemoteHostExecutor(self._target.remote_host)

        for target_device_id, source_device_id in self._target.device_mapping.items():
            if executable_for_disks:
                executable_for_disks(
                    remote_executor,
                    (source_device_id, self._source.remote_host.system_info['block_devices'][source_device_id]),
                    (target_device_id, self._target.remote_host.system_info['block_devices'][target_device_id]),
                )

            if executable_for_partitions:
                for partition_device_id, partition_device \
                        in self._source.remote_host.system_info['block_devices'][source_device_id]['children'].items():
                    executable_for_partitions(
                        remote_executor,
                        (source_device_id, self._source.remote_host.system_info['block_devices'][source_device_id]),
                        (target_device_id, self._target.remote_host.system_info['block_devices'][target_device_id]),
                        (partition_device_id, partition_device),
                    )

    def _execute_on_every_partition(self, executable):
        """
        executes the given executable on all partitions
        
        :param executable: a function which takes the parameters: remote_executor, source_device, 
        target_device, partition_device
        :type executable: (self: Any, RemoteExecutor, (str, dict), (str, dict), (str, dict)) -> None
        """
        return self._execute_on_every_device(None, executable)
