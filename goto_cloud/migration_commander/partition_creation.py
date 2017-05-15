from remote_execution.public import RemoteHostExecutor

from remote_host_command.public import RemoteHostCommand

from .device_modification import DeviceModifyingCommand


class CreatePartitionsCommand(DeviceModifyingCommand):
    """
    takes care of creating the partitions on the target system
    """
    class CanNotCreatePartitionException(DeviceModifyingCommand.CommandExecutionException):
        """
        is called if a partition can not be created, for whatever reason
        """
        COMMAND_DOES = 'create the partitions'

    ERROR_REPORT_EXCEPTION_CLASS = CanNotCreatePartitionException

    READ_PARTITION_TABLE_COMMAND = RemoteHostCommand('sudo sfdisk -d {DEVICE}')
    WRITE_PARTITION_TABLE_COMMAND = RemoteHostCommand('echo "{PARTITION_TABLE}" | sudo sfdisk {DEVICE}')

    def _execute(self):
        self.source_remote_executor = RemoteHostExecutor(self._source.remote_host)
        self._execute_on_every_device(self._replicate_partition_table, None, include_swap=True)
        self.source_remote_executor.close()
        self.source_remote_executor = None

    @DeviceModifyingCommand._collect_errors
    def _replicate_partition_table(self, remote_executor, source_device, target_device):
        """
        replicates the partition table of the source device and applies it to the target device

        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor 
        :param source_device: the source device
        :type source_device: (str, dict)
        :param target_device: the target device
        :type target_device: (str, dict)
        """
        self._write_partition_table(
            remote_executor,
            target_device[0],
            self._read_partition_table(
                self.source_remote_executor,
                source_device[0],
            )
        )

    def _write_partition_table(self, remote_executor, target_device_id, partition_table):
        remote_executor.execute(
            self.WRITE_PARTITION_TABLE_COMMAND.render(
                partition_table=self._make_string_echo_safe(partition_table),
                device='/dev/{device_id}'.format(device_id=target_device_id)
            )
        )

    def _read_partition_table(self, source_remote_executor, source_device_id):
        return source_remote_executor.execute(
            self.READ_PARTITION_TABLE_COMMAND.render(
                device='/dev/{device_id}'.format(device_id=source_device_id)
            )
        )

    def _make_string_echo_safe(self, string):
        return string.replace('"', '\\"')
