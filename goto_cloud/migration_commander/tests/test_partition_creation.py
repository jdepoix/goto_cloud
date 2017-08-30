from test_assets.public import TestAsset

from ..partition_creation import CreatePartitionsCommand

from .utils import MigrationCommanderTestCase


class TestCreatePartitionsCommand(MigrationCommanderTestCase):
    def _init_test_data(self, source_host, target_host):
        super()._init_test_data(source_host, target_host)
        TestAsset.REMOTE_HOST_MOCKS['ubuntu16'].add_command(
            'sudo sfdisk -d /dev/vda',
            'PART "doesn\'t contain a valid partition table"'
        )
        TestAsset.REMOTE_HOST_MOCKS['ubuntu16'].add_command(
            'sudo sfdisk -d /dev/vdb',
            'PART "TABLE"'
        )
        TestAsset.REMOTE_HOST_MOCKS['ubuntu16'].add_command(
            'sudo sfdisk -d /dev/vdc',
            'PART "TABLE"'
        )
        TestAsset.REMOTE_HOST_MOCKS['target__device_identification'].add_command(
            'sfdisk',
            ''
        )

    def test_execute__source_part_table_read(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        CreatePartitionsCommand(self.source).execute()

        self.assertIn('sudo sfdisk -d /dev/vda', self.executed_commands)
        self.assertIn('sudo sfdisk -d /dev/vdb', self.executed_commands)
        self.assertIn('sudo sfdisk -d /dev/vdc', self.executed_commands)

    def test_execute__target_part_table_write(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        CreatePartitionsCommand(self.source).execute()

        self.assertIn('echo "PART \\"TABLE\\"" | sudo sfdisk /dev/vdc', self.executed_commands)
        self.assertIn('echo "PART \\"TABLE\\"" | sudo sfdisk /dev/vdd', self.executed_commands)

    def test_execute__don_t_write_invalid_part_table(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        CreatePartitionsCommand(self.source).execute()

        self.assertNotIn(
            'echo "PART \\"doesn\'t contain a valid partition table\\"" | sudo sfdisk /dev/vdb',
            self.executed_commands
        )
