from command.public import SourceCommand

from remote_execution.public import RemoteHostExecutor

from .remote_file_edit import RemoteFileEditor
from .source_file_location_resolving import SourceFileLocationResolver


class SshConfigAdjustmentCommand(SourceCommand):
    SSHD_CONFIG_LOCATION = '/etc/ssh/sshd_config'

    def _execute(self):
        self._replace_ips_in_sshd_config()

    def _replace_ips_in_sshd_config(self):
        for interface in self._target.blueprint['network_interfaces']:
            self._replace_ip_in_sshd_config(
                self._source.remote_host.system_info['network']['interfaces'][interface['source_interface']]['ip'],
                interface['ip']
            )

    def _replace_ip_in_sshd_config(self, old_ip, new_ip):
        RemoteFileEditor(RemoteHostExecutor(self._target.remote_host)).edit(
            SourceFileLocationResolver(self._source).resolve(self.SSHD_CONFIG_LOCATION),
            old_ip,
            new_ip
        )
