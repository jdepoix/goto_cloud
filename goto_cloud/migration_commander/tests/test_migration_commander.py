from unittest.mock import patch

from remote_host.public import RemoteHost

from migration_plan_parsing.public import MigrationPlanParser

from source.public import Source

from test_assets.public import TestAsset

from command.public import SourceCommand

from migration_commander.migration_commander import MigrationCommander

from .utils import MigrationCommanderTestCase


class CreateTargetCommandMock(SourceCommand):
    def _execute(self):
        self._target.remote_host = RemoteHost.objects.create(address='target__device_identification')
        self._target.save()


class NoopCommand(SourceCommand):
    def _execute(self):
        pass


class TestMigrationCommander(MigrationCommanderTestCase):
    def _init_test_data(self, source_host, target_host):
        MigrationPlanParser().parse(TestAsset.MIGRATION_PLAN_MOCK)

        self.source = Source.objects.get(remote_host__address=source_host)

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
        TestAsset.REMOTE_HOST_MOCKS[target_host].add_command(
            'sfdisk',
            ''
        )

    @patch.dict(MigrationCommander._COMMAND_DRIVER, {
        Source.Status.CREATE_TARGET: CreateTargetCommandMock,
        Source.Status.STOP_TARGET: NoopCommand,
        Source.Status.DELETE_BOOTSTRAP_VOLUME: NoopCommand,
        Source.Status.DELETE_BOOTSTRAP_NETWORK_INTERFACE: NoopCommand,
        Source.Status.CONFIGURE_BOOT_DEVICE: NoopCommand,
        Source.Status.START_TARGET: NoopCommand,
    })
    def test_execute(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        MigrationCommander(self.source).execute()
        self.assertEqual(self.source.status, Source.Status.SYNC)
        MigrationCommander(self.source).increment_status_and_execute()
        self.assertEqual(self.source.status, Source.Status.LIVE)
