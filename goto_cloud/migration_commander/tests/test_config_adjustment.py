from test_assets.public import TestAsset

from ..config_adjustment import SshConfigAdjustmentCommand
from ..remote_file_edit import RemoteFileEditor
from ..tests.utils import MigrationCommanderTestCase


class TestSshConfigAdjustment(MigrationCommanderTestCase):
    SSHD_CONFIG = (
        'ListenAddress 10.17.32.4:22\n'
        '\n'
        'PermitRootLogin No\n'
        'Protocol 2\n'
        'AuthorizedKeysFile .ssh/authorized_keys\n'
        'GSSAPIAuthentication no\n'
        'HostbasedAuthentication no\n'
        'KerberosAuthentication no\n'
        'PasswordAuthentication no\n'
        'PubkeyAuthentication yes\n'
        'RhostsRSAAuthentication no\n'
        'RSAAuthentication no\n'
        'UsePAM no\n'
        'UseDNS no\n'
        '\n'
        'PrintMotd no\n'
        '\n'
        'MaxSessions 512\n'
        'MaxStartups 512:30:768\n'
        '\n'
        'Subsystem sftp internal-sftp\n'
        '\n'
        'Match Group sftp\n'
        'ChrootDirectory %h\n'
        'ForceCommand internal-sftp\n'
        'AllowTcpForwarding no\n'
        'PasswordAuthentication no'
    )

    def _init_test_data(self, source_host, target_host):
        super()._init_test_data(source_host, target_host)
        self.executed_commands.clear()
        TestAsset.REMOTE_HOST_MOCKS['target__device_identification'].add_command(
            'sudo cat {mountpoint}{config_path}'.format(
                mountpoint=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint'],
                config_path=SshConfigAdjustmentCommand.SSHD_CONFIG_LOCATION,
            ),
            self.SSHD_CONFIG
        )

    def test_execute__sshd_config_edited(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        SshConfigAdjustmentCommand(self.source).execute()

        self.assertIn(
            RemoteFileEditor._WRITE_FILE.render(
                file=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
                    + SshConfigAdjustmentCommand.SSHD_CONFIG_LOCATION,
                file_content=self.SSHD_CONFIG.replace(
                    '10.17.32.4',
                    next(
                        interface['ip']
                        for interface in self.source.target.blueprint['network_interfaces']
                        if interface['source_interface'] == 'eth0'
                    )
                ),
            ),
            self.executed_commands
        )
