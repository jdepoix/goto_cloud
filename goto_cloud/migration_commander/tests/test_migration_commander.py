from remote_host.public import RemoteHost

from migration_plan_parsing.public import MigrationPlanParser

from source.public import Source

from test_assets.public import TestAsset

from ..migration_commander import MigrationCommander

from .utils import MigrationCommanderTestCase


class TestMigrationCommander(MigrationCommanderTestCase):
    def _init_test_data(self, source_host, target_host):
        MigrationPlanParser().parse(TestAsset.MIGRATION_PLAN_MOCK)

        self.source = Source.objects.get(remote_host__address=source_host)
        self.source.target.remote_host = RemoteHost.objects.create(address=target_host)
        self.source.target.save()

    def test_execute(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        MigrationCommander(self.source).execute()
        self.assertEqual(self.source.status, Source.Status.SYNCING)
        MigrationCommander(self.source).increment_status_and_execute()
        self.assertEqual(self.source.status, Source.Status.LIVE)
