from django.test import TestCase

from migration_plan_parsing.public import MigrationPlanParser

from remote_host.public import RemoteHost

from source.public import Source

from test_assets.public import TestAsset

from ..device_identification import DeviceIdentificationCommand
from ..partition_creation import CreatePartitionsCommand
from ..target_system_info_inspection import GetTargetSystemInfoCommand

from .utils import PatchTrackedRemoteExecution


class TestCreatePartitionsCommand(TestCase, metaclass=PatchTrackedRemoteExecution):
    def _init_test_data(self, source_host, target_host):
        self.executed_commands.clear()

        MigrationPlanParser().parse(TestAsset.MIGRATION_PLAN_MOCK)

        self.source = Source.objects.get(remote_host__address=source_host)
        self.source.target.remote_host = RemoteHost.objects.create(address=target_host)
        self.source.target.save()

        GetTargetSystemInfoCommand(self.source).execute()
        DeviceIdentificationCommand(self.source).execute()

    def test_execute(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        CreatePartitionsCommand(self.source).execute()

        self.assertIn('echo -e \"n\n\n1\n2048\n20971519\nw\n\" | sudo fdisk /dev/vdb', self.executed_commands)
        self.assertIn('echo -e \"n\n\n1\n2048\n10487807\nw\n\" | sudo fdisk /dev/vdd', self.executed_commands)
        self.assertIn('echo -e \"n\n\n2\n10487808\n20971519\nw\n\" | sudo fdisk /dev/vdd', self.executed_commands)
        self.assertIn('echo -e \"a\nw\n\" | sudo fdisk /dev/vdb', self.executed_commands)

    def test_execute__booatable_flag_with_multiple_partitions(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.source.remote_host.system_info['block_devices']['vda']['children']['vda2'] = \
            self.source.remote_host.system_info['block_devices']['vda']['children']['vda1']

        CreatePartitionsCommand(self.source).execute()

        self.assertIn('echo -e \"n\n\n1\n2048\n20971519\nw\n\" | sudo fdisk /dev/vdb', self.executed_commands)
        self.assertIn('echo -e \"n\n\n1\n2048\n10487807\nw\n\" | sudo fdisk /dev/vdd', self.executed_commands)
        self.assertIn('echo -e \"n\n\n2\n10487808\n20971519\nw\n\" | sudo fdisk /dev/vdd', self.executed_commands)
        self.assertIn('echo -e \"a\n1\nw\n\" | sudo fdisk /dev/vdb', self.executed_commands)

    def test_execute__can_not_create_children(self):
        self._init_test_data('ubuntu16__lvm', 'target__device_identification')

        with self.assertRaises(CreatePartitionsCommand.CanNotCreatePartitionException):
            CreatePartitionsCommand(self.source).execute()

    def test_execute__invalid_partition_type(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        source_remote_host = self.source.remote_host
        source_remote_host.system_info['block_devices']['vda']['children']['vda1']['type'] = 'unknown'
        source_remote_host.save()

        with self.assertRaises(CreatePartitionsCommand.CanNotCreatePartitionException):
            CreatePartitionsCommand(self.source).execute()
