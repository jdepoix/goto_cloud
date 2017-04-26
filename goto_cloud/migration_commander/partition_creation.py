from remote_execution.public import RemoteHostExecutor

from remote_host_command.public import RemoteHostCommand

from .device_modification import DeviceModifyingCommand


class CreatePartitionsCommand(DeviceModifyingCommand):
    """
    takes care of creating the partitions on the target system
    """
    class CanNotCreatePartitionException(Exception):
        """
        is called if a partition can not be created, for whatever reason
        """
        pass

    def _execute(self):
        self._execute_on_every_partition(self._create_partition)

    def _handle_error_report(self, error_report):
        raise CreatePartitionsCommand.CanNotCreatePartitionException(
            'While trying to create the partitions, the following errors occurred. Please resolves these manually '
            'and then skip this step:\n{errors}'.format(errors=error_report)
        )

    @DeviceModifyingCommand._collect_errors
    def _execute_create_partition(self, remote_executor, partition_number, start, end, parent_device):
        """
        executes the create partition command using the given remote executor and context
        
        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor
        :param partition_number: the partition number
        :type partition_number: str
        :param start: where does the partition start
        :type start: int
        :param end: where does the partition end
        :type end: int
        :param parent_device: the parent device of the partition
        :type parent_device: str
        """
        remote_executor.execute(
            RemoteHostCommand(self._target.blueprint['commands']['create_partition']).render(
                partition_number=partition_number,
                start=start,
                end=end,
                device=parent_device,
            )
        )

    @DeviceModifyingCommand._collect_errors
    def _execute_tag_partition_bootable(self, remote_executor, source_device, partition_number, parent_device):
        """
        executes the tag partition bootable command using the given remote executor and context

        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor
        :param source_device: the source device
        :type source_device: dict
        :param partition_number: the partition number
        :type partition_number: str
        :param parent_device: the parent device of the partition
        :type parent_device: str
        """
        remote_executor.execute(
            RemoteHostCommand(self._target.blueprint['commands']['tag_partition_bootable']).render(
                parent_device=parent_device,
                **({
                    'partition_number': partition_number,
                } if len(source_device['children']) > 1 else {})
            )
        )

    def _create_partition(
        self, remote_executor, source_device, target_device, source_partition_device, target_partition_device
    ):
        """
        creates a partition
        
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
        if source_partition_device[1]['type'] == 'part':
            parent_device = '/dev/{device_id}'.format(device_id=target_device[0])

            self._execute_create_partition(
                remote_executor,
                target_partition_device[0][-1],
                source_partition_device[1]['start'],
                source_partition_device[1]['end'],
                parent_device,
            )

            if source_partition_device[1]['bootable']:
                self._execute_tag_partition_bootable(
                    remote_executor, source_device[1], target_partition_device[0][-1], parent_device,
                )

            if source_partition_device[1]['children']:
                self._add_error(
                    'The device {device_id} seems to have children, which can not be replicated to '
                    '{target_device_id} automatically. '
                    'These children should be replicated:\n{children}'.format(
                        device_id=source_partition_device[0],
                        target_device_id=target_device[0],
                        children=str(source_partition_device[1]['children'])
                    )
                )
        else:
            self._add_error(
                'The device {device_id} is not of type partition and therefore can\'t be replicated to '
                '{target_partition_device_id}'.format(
                    device_id=source_partition_device[0],
                    target_partition_device_id=target_partition_device[0]
                )
            )
