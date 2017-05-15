from ..filesystem_creation import CreateFilesystemsCommand

from .utils import MigrationCommanderTestCase


class TestCreateFilesystemsCommand(MigrationCommanderTestCase):
    def test_execute(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        CreateFilesystemsCommand(self.source).execute()

        self.assertIn('sudo mkfs.ext4 -U 549c8755-2757-446e-8c78-f76b50491f21 -F /dev/vdb1', self.executed_commands)
        self.assertIn('sudo mkfs.ext3 -U d04ba532-cd2d-4406-a5ef-114acf019cc8 -F /dev/vdc', self.executed_commands)
        self.assertIn('sudo mkfs.ext4 -U 53ad2170-488d-481a-a6ab-5ce0e538f247 -F /dev/vdd1', self.executed_commands)
        self.assertIn('sudo mkfs.ext4 -U bcab224c-8407-4783-8cea-f9ea4be3fabf -F /dev/vdd2', self.executed_commands)

    def test_execute__non_supported_filesystem(self):
        self._init_test_data('ubuntu16__lvm', 'target__device_identification')

        with self.assertRaises(CreateFilesystemsCommand.UnsupportedFilesystemException):
            CreateFilesystemsCommand(self.source).execute()

    def test_execute__swap_not_created(self):
        self._init_test_data('ubuntu12', 'target__device_identification')

        CreateFilesystemsCommand(self.source).execute()
