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
        target_device and returns a string with an error message, in case there was an error
        :type executable_for_disks: (self: Any, RemoteExecutor, (str, dict), (str, dict)) -> str
        :param executable: a function which takes the parameters: remote_executor, source_device, 
        target_device, partition_device and returns a string with an error message, in case 
        there was an error
        :type executable_for_partitions: (self: Any, RemoteExecutor, (str, dict), (str, dict), (str, dict)) -> str
        :return: a list of errors which occurred in the executables
        :rtype: [str]
        """
        collected_errors = []
        remote_executor = RemoteHostExecutor(self._target.remote_host)

        for target_device_id, source_device_id in self._target.device_mapping.items():
            if executable_for_disks:
                self._add_errors(
                    collected_errors,
                    executable_for_disks(
                        remote_executor,
                        (source_device_id, self._source.remote_host.system_info['block_devices'][source_device_id]),
                        (target_device_id, self._target.remote_host.system_info['block_devices'][target_device_id]),
                    )
                )

            if executable_for_partitions:
                for partition_device_id, partition_device \
                        in self._source.remote_host.system_info['block_devices'][source_device_id]['children'].items():
                    self._add_errors(
                        collected_errors,
                        executable_for_partitions(
                            remote_executor,
                            (source_device_id, self._source.remote_host.system_info['block_devices'][source_device_id]),
                            (target_device_id, self._target.remote_host.system_info['block_devices'][target_device_id]),
                            (partition_device_id, partition_device),
                        )
                    )

        return collected_errors

    def _execute_on_every_partition(self, executable):
        """
        executes the given executable on all partitions
        
        :param executable: a function which takes the parameters: remote_executor, source_device, 
        target_device, partition_device and returns a string with an error message, in case 
        there was an error
        :type executable: (self: Any, RemoteExecutor, (str, dict), (str, dict), (str, dict)) -> str
        :return: a list of errors which occurred in the executables
        :rtype: [str]
        """
        return self._execute_on_every_device(None, executable)

    def _execute_and_return_errors(self, executable):
        """
        executes something and in case an exception is thrown, it continues execution and returns the exception as a
        string
        
        :param executable: a callable
        :type executable: () -> Any
        :return: error message
        :rtype: str
        """
        try:
            executable()
        except Exception as e:
            return str(e)

    def _add_errors(self, errors, new_error):
        if new_error:
            if isinstance(new_error, list):
                errors.extend(new_error)
            else:
                errors.append(new_error)
