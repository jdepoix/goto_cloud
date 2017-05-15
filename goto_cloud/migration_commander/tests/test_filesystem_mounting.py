from unittest.mock import patch, Mock

from ..filesystem_mounting import FilesystemMountCommand
from ..device_identification import DeviceIdentificationCommand

from .utils import MigrationCommanderTestCase


class TestFilesystemMountCommand(MigrationCommanderTestCase):
    def test_execute__mount_applied(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        FilesystemMountCommand(self.source).execute()

        self.assertIn('sudo mount -a', self.executed_commands)

    def test_execute__fstab_edited(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        FilesystemMountCommand(self.source).execute()

        self.assertIn(
            (
                'sudo bash -c "echo -e \\"'
                'UUID=549c8755-2757-446e-8c78-f76b50491f21\t'
                + DeviceIdentificationCommand._map_mountpoint('/')
                + '\text4\tdefaults\t0\t2'
                '\\" >> /etc/fstab"'
            ),
            self.executed_commands
        )
        self.assertIn(
            (
                'sudo bash -c "echo -e \\"'
                'UUID=53ad2170-488d-481a-a6ab-5ce0e538f247\t'
                + DeviceIdentificationCommand._map_mountpoint('/mnt/vdc1')
                + '\text4\tdefaults\t0\t2'
                '\\" >> /etc/fstab"'
            ),
            self.executed_commands
        )
        self.assertIn(
            (
                'sudo bash -c "echo -e \\"'
                'UUID=bcab224c-8407-4783-8cea-f9ea4be3fabf\t'
                + DeviceIdentificationCommand._map_mountpoint('/mnt/vdc2')
                + '\text4\tdefaults\t0\t2'
                '\\" >> /etc/fstab"'
            ),
            self.executed_commands
        )

    def test_execute__mount_dirs_created(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        FilesystemMountCommand(self.source).execute()

        self.assertIn(
            'sudo mkdir -p ' + DeviceIdentificationCommand._map_mountpoint('/'),
            self.executed_commands
        )
        self.assertIn(
            'sudo mkdir -p ' + DeviceIdentificationCommand._map_mountpoint('/mnt/vdc1'),
            self.executed_commands
        )
        self.assertIn(
            'sudo mkdir -p ' + DeviceIdentificationCommand._map_mountpoint('/mnt/vdc2'),
            self.executed_commands
        )

    @patch(
        'migration_commander.remote_file_edit.RemoteFileEditor.append',
        Mock(side_effect=Exception())
    )
    def test_execute__failed(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        with self.assertRaises(FilesystemMountCommand.MountingException):
            FilesystemMountCommand(self.source).execute()

    def test_execute__with_swap(self):
        self._init_test_data('ubuntu12', 'target__device_identification')

        FilesystemMountCommand(self.source).execute()
