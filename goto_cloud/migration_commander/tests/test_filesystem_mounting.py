from unittest.mock import patch, Mock

from django.test import TestCase

from migration_plan_parsing.public import MigrationPlanParser

from source.public import Source

from remote_host.public import RemoteHost

from test_assets.public import TestAsset

from ..target_system_info_inspection import GetTargetSystemInfoCommand
from migration_commander.filesystem_mounting import FilesystemMountCommand
from ..device_identification import DeviceIdentificationCommand

from .utils import PatchTrackedRemoteExecution


class TestFilesystemMountCommand(TestCase, metaclass=PatchTrackedRemoteExecution):
    def _init_test_data(self, source_host, target_host):
        MigrationPlanParser().parse(TestAsset.MIGRATION_PLAN_MOCK)

        self.source = Source.objects.get(remote_host__address=source_host)
        self.source.target.remote_host = RemoteHost.objects.create(address=target_host)
        self.source.target.save()

        GetTargetSystemInfoCommand(self.source).execute()
        DeviceIdentificationCommand(self.source).execute()

        self.source.target.save()

    def test_execute__mount_applied(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        FilesystemMountCommand(self.source).execute()

        self.assertIn('sudo mount -a', self.executed_commands)

    def test_execute__fstab_edited(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        FilesystemMountCommand(self.source).execute()

        self.assertIn(
            (
                'sudo echo -e "'
                'UUID=549c8755-2757-446e-8c78-f76b50491f21\t/mnt/' + str(hash('/')) + '\text4\tdefaults\t0\t2'
                '" >> /etc/fstab'
            ),
            self.executed_commands
        )
        self.assertIn(
            (
                'sudo echo -e "'
                'UUID=53ad2170-488d-481a-a6ab-5ce0e538f247\t/mnt/' + str(hash('/mnt/vdc1')) + '\text4\tdefaults\t0\t2'
                '" >> /etc/fstab'
            ),
            self.executed_commands
        )
        self.assertIn(
            (
                'sudo echo -e "'
                'UUID=bcab224c-8407-4783-8cea-f9ea4be3fabf\t/mnt/' + str(hash('/mnt/vdc2')) + '\text4\tdefaults\t0\t2'
                '" >> /etc/fstab'
            ),
            self.executed_commands
        )

    @patch(
        'migration_commander.default_remote_host_commands.DefaultRemoteHostCommand.ADD_FSTAB_ENTRY.render',
        Mock(side_effect=Exception())
    )
    def test_execute__failed(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        with self.assertRaises(FilesystemMountCommand.MountingException):
            FilesystemMountCommand(self.source).execute()
