from django.test import TestCase

from source.public import Source

from remote_host.public import RemoteHost

from migration_plan_parsing.public import MigrationPlanParser

from test_assets.public import TestAsset

from ..filesystem_creation import CreateFilesystemsCommand
from ..target_system_info_inspection import GetTargetSystemInfoCommand

from .utils import PatchTrackedRemoteExecution


class TestCreateFilesystemsCommand(TestCase, metaclass=PatchTrackedRemoteExecution):
    def _init_test_data(self, source_host, target_host):
        MigrationPlanParser().parse(TestAsset.MIGRATION_PLAN_MOCK)

        self.source = Source.objects.get(remote_host__address=source_host)
        self.source.target.remote_host = RemoteHost.objects.create(address=target_host)
        self.source.target.save()

        GetTargetSystemInfoCommand(self.source).execute()

        self.source.target.device_mapping = {
            'vdb': 'vda',
            'vdc': 'vdb',
            'vdd': 'vdc',
        }
        self.source.target.save()

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
