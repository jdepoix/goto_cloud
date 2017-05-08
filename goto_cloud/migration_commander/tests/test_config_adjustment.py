from test_assets.public import TestAsset

from ..config_adjustment import SshConfigAdjustmentCommand, FstabAdjustmentCommand
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
                    'ListenAddress',
                    '# ListenAddress'
                ),
            ),
            self.executed_commands
        )


class TestFstabAdjustment(MigrationCommanderTestCase):
    FSTAB = (
        '/dev/vda1	/		ext4    errors=remount-ro 	0       1\n'
        '/dev/vdc1	/mnt/vdc1	ext4	defaults		0	2\n'
        '/dev/vdc2	/mnt/vdc2	ext4	defaults		0	2'
    )

    def _init_test_data(self, source_host, target_host):
        super()._init_test_data(source_host, target_host)
        TestAsset.REMOTE_HOST_MOCKS['target__device_identification'].add_command(
            'sudo cat {mountpoint}{config_path}'.format(
                mountpoint=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint'],
                config_path=FstabAdjustmentCommand.FSTAB_LOCATION,
            ),
            self.FSTAB
        )

    def test_execute(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        FstabAdjustmentCommand(self.source).execute()

        self.assertIn(
            RemoteFileEditor._WRITE_FILE.render(
                file=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
                    + FstabAdjustmentCommand.FSTAB_LOCATION,
                file_content=self.FSTAB.replace(
                    '/dev/vda1', 'UUID=549c8755-2757-446e-8c78-f76b50491f21'
                )
            ),
            self.executed_commands
        )
        self.assertIn(
            RemoteFileEditor._WRITE_FILE.render(
                file=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
                     + FstabAdjustmentCommand.FSTAB_LOCATION,
                file_content=self.FSTAB.replace(
                    '/dev/vdc1', 'UUID=53ad2170-488d-481a-a6ab-5ce0e538f247'
                )
            ),
            self.executed_commands
        )
        self.assertIn(
            RemoteFileEditor._WRITE_FILE.render(
                file=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
                     + FstabAdjustmentCommand.FSTAB_LOCATION,
                file_content=self.FSTAB.replace(
                    '/dev/vdc2', 'UUID=bcab224c-8407-4783-8cea-f9ea4be3fabf'
                )
            ),
            self.executed_commands
        )
