from command.public import SourceCommand

from remote_execution.public import RemoteHostExecutor

from .device_modification import DeviceModifyingCommand
from .remote_file_edit import RemoteFileEditor
from .source_file_location_resolving import SourceFileLocationResolver

# TODO docs!
class SshConfigAdjustmentCommand(SourceCommand):
    class SshConfigAdjustmentException(DeviceModifyingCommand.CommandExecutionException):
        COMMAND_DOES = 'adjust ssh config'

    ERROR_REPORT_EXCEPTION_CLASS = SshConfigAdjustmentException
    SSHD_CONFIG_LOCATION = '/etc/ssh/sshd_config'

    def _execute(self):
        self._replace_ips_in_sshd_config()

    def _handle_error_report(self, error_report):
        # TODO
        raise Exception(error_report)

    def _replace_ips_in_sshd_config(self):
        remote_executor = RemoteHostExecutor(self._target.remote_host)

        for interface in self._target.blueprint['network_interfaces']:
            self._replace_ip_in_sshd_config(
                remote_executor,
                self._source.remote_host.system_info['network']['interfaces'][interface['source_interface']]['ip'],
                interface['ip']
            )

    def _replace_ip_in_sshd_config(self, remote_executor, old_ip, new_ip):
        RemoteFileEditor(remote_executor).edit(
            SourceFileLocationResolver(self._source).resolve(self.SSHD_CONFIG_LOCATION),
            old_ip,
            new_ip
        )


# TODO docs!
class FstabAdjustmentCommand(DeviceModifyingCommand):
    class FstabAdjustmentException(DeviceModifyingCommand.CommandExecutionException):
        COMMAND_DOES = 'adjust fstab'

    ERROR_REPORT_EXCEPTION_CLASS = FstabAdjustmentException
    FSTAB_LOCATION = '/etc/fstab'

    def _execute(self):
        self._execute_on_every_partition(self._replace_partition_in_fstab)
        self._execute_on_every_device(self._replace_disk_in_fstab)

    def _replace_disk_in_fstab(
        self, remote_executor, source_device, target_device
    ):
        """
        replaces a disks information in fstab with the information of the new device
        
        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor 
        :param source_device: the source device
        :type source_device: (str, dict)
        :param target_device: the target device
        :type target_device_id: (str, dict)
        """
        self._replace_device_information(
            remote_executor,
            source_device[0],
            target_device[0],
            source_device[1]['uuid'],
            source_device[1]['label'],
        )

    def _replace_partition_in_fstab(
        self, remote_executor, source_device, target_device, partition_device, target_partition_device
    ):
        """
        replaces a partitions information in fstab with the information of the new device
        
        :param remote_executor: remote executor to use for execution
        :type remote_executor: RemoteHostExecutor 
        :param source_device: the source device
        :type source_device: (str, dict)
        :param target_device: the target device
        :type target_device_id: (str, dict)
        :param partition_device: the original partition device
        :type partition_device: (str, dict)
        :param target_partition_device: the target partition device
        :type target_partition_device: (str, dict)
        """
        self._replace_device_information(
            remote_executor,
            partition_device[0],
            target_partition_device[0],
            partition_device[1]['uuid'],
            partition_device[1]['label'],
        )

    @DeviceModifyingCommand._collect_errors
    def _replace_device_information(self, remote_executor, old_device_id, device_id, uuid=None, label=None):
        RemoteFileEditor(remote_executor).edit(
            SourceFileLocationResolver(self._source).resolve(self.FSTAB_LOCATION),
            '/dev/{device_id}'.format(device_id=old_device_id),
            'UUID={uuid}'.format(uuid=uuid)
                if uuid
                else 'LABEL={label}'.format(label=label)
                    if label
                    else '/dev/{device_id}'.format(device_id=device_id),
        )
