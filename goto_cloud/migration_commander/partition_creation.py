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
        errors = self._execute_on_every_partition(self._create_partition)

        if errors:
            raise CreatePartitionsCommand.CanNotCreatePartitionException(
                'While trying to create the partitions, the following errors occurred. Please resolves these manually '
                'and then skip this step:\n{errors}'.format(
                    errors='\n\n-------------------------------------------------------------\n'.join(errors)
                )
            )

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
        :return: errors which occurred
        :rtype: str
        """
        return self._execute_and_return_errors(
            lambda: remote_executor.execute(
                RemoteHostCommand(self._target.blueprint['commands']['create_partition']).render(
                    partition_number=partition_number,
                    start=start,
                    end=end,
                    device=parent_device,
                )
            )
        )

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
        :return: errors which occurred
        :rtype: str
        """
        return self._execute_and_return_errors(
            lambda: remote_executor.execute(
                RemoteHostCommand(self._target.blueprint['commands']['tag_partition_bootable']).render(
                    parent_device=parent_device,
                    **({
                        'partition_number': partition_number,
                    } if len(source_device['children']) > 1 else {})
                )
            )
        )

    def _create_partition(self, remote_executor, source_device, target_device, partition_device):
        """
        creates a partition
        
        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor 
        :param source_device: the source device
        :type source_device: (str, dict)
        :param target_device: the target device
        :type target_device: (str, dict)
        :param partition_device: the original partition device
        :type partition_device: (str, dict)
        :return: a list of errors which occurred during execution (in case it did...)
        :rtype: [str]
        """
        errors = []

        if partition_device[1]['type'] == 'part':
            parent_device = '/dev/{device_id}'.format(device_id=target_device[0])

            self._add_errors(
                errors,
                self._execute_create_partition(
                    remote_executor,
                    partition_device[0][-1],
                    partition_device[1]['start'],
                    partition_device[1]['end'],
                    parent_device
                )
            )

            if partition_device[1]['bootable']:
                self._add_errors(
                    errors,
                    self._execute_tag_partition_bootable(
                        remote_executor, source_device[1], partition_device[0][-1], parent_device,
                    )
                )

            if partition_device[1]['children']:
                errors.append(
                    'The device {device_id} seems to have children, which can not be replicated to '
                    '{target_device_id} automatically. '
                    'These children should be replicated:\n{children}'.format(
                        device_id=partition_device[0],
                        target_device_id=target_device[0],
                        children=str(partition_device[1]['children'])
                    )
                )
        else:
            errors.append(
                'The device {device_id} is not of type partition and therefore can\'t be replicated to '
                '{target_device_id}'.format(
                    device_id=partition_device[0],
                    target_device_id=target_device[0]
                )
            )

        return errors
