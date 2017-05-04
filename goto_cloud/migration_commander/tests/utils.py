from unittest.mock import patch

from django.test import TestCase

from migration_plan_parsing.public import MigrationPlanParser

from remote_host.public import RemoteHost

from source.public import Source

from test_assets.public import TestAsset

from ..device_identification import DeviceIdentificationCommand
from ..target_system_info_inspection import GetTargetSystemInfoCommand


class PatchTrackedRemoteExecution(TestAsset.PatchRemoteHostMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executed_commands = set()
        def tracked_mocked_execute(remote_host, command):
            self.executed_commands.add(command)
            return TestAsset.PatchRemoteHostMeta.MOCKED_EXECUTE(remote_host, command)

        patch(
            'remote_execution.remote_execution.SshRemoteExecutor._execute',
            tracked_mocked_execute
        )(self)


class MigrationCommanderTestCase(TestCase, metaclass=PatchTrackedRemoteExecution):
    def setUp(self):
        self.executed_commands.clear()

    def _init_test_data(self, source_host, target_host):
        MigrationPlanParser().parse(TestAsset.MIGRATION_PLAN_MOCK)

        self.source = Source.objects.get(remote_host__address=source_host)
        self.source.target.remote_host = RemoteHost.objects.create(address=target_host)
        self.source.target.save()

        GetTargetSystemInfoCommand(self.source).execute()
        DeviceIdentificationCommand(self.source).execute()

        self.executed_commands.clear()
