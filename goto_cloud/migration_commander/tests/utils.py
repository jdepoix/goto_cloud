from django.test import TestCase

from migration_plan_parsing.public import MigrationPlanParser

from remote_host.public import RemoteHost

from source.public import Source

from test_assets.public import TestAsset

from ..device_identification import DeviceIdentificationCommand
from ..target_system_info_inspection import GetTargetSystemInfoCommand


class MigrationCommanderTestCase(TestCase, metaclass=TestAsset.PatchTrackedRemoteExecutionMeta):
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
