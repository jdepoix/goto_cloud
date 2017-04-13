from django.test import TestCase

from remote_host_mocks.public import PatchRemoteHostMeta

from migration_run.public import MigrationRun

from target.public import Target

from source.public import Source

from migration_plan.public import MigrationPlan

from ..migration_plan_parsing import MigrationPlanParser

from .assets.migration_plan_mock import MIGRATION_PLAN_MOCK


def failing_method(*args, **kwargs):
    raise Exception()


class TestMigrationPlanParser(TestCase, metaclass=PatchRemoteHostMeta):
    def test_parse(self):
        returned_migration_run = MigrationPlanParser().parse(MIGRATION_PLAN_MOCK)

        migration_plan = MigrationPlan.objects.first()
        migration_run = MigrationRun.objects.first()

        self.assertEquals(returned_migration_run, migration_run)

        self.assertEquals(migration_plan.plan, MIGRATION_PLAN_MOCK)
        self.assertEquals(migration_run.plan, migration_plan)

        self.assertEquals(Source.objects.count(), len(MIGRATION_PLAN_MOCK['sources']))
        for source in Source.objects.all():
            self.assertIsNotNone(source.target)
            self.assertIsNotNone(source.remote_host)
            self.assertEquals(source.migration_run, migration_run)

        self.assertEquals(Target.objects.count(), len(MIGRATION_PLAN_MOCK['sources']))

    def test_parse__delete(self):
        migration_plan_parser = MigrationPlanParser()

        migration_plan_parser.parse(MIGRATION_PLAN_MOCK)
        migration_plan_parser.delete()

        self.assertEquals(MigrationPlan.objects.count(), 0)
        self.assertEquals(MigrationRun.objects.count(), 0)
        self.assertEquals(Source.objects.count(), 0)
        self.assertEquals(Target.objects.count(), 0)

    def test_parse__delete_on_failure(self):
        migration_plan_parser = MigrationPlanParser()
        migration_plan_parser._create_migration_run = failing_method

        with self.assertRaises(Exception):
            migration_plan_parser.parse(MIGRATION_PLAN_MOCK)

        self.assertEquals(MigrationPlan.objects.count(), 0)
        self.assertEquals(MigrationRun.objects.count(), 0)
        self.assertEquals(Source.objects.count(), 0)
        self.assertEquals(Target.objects.count(), 0)
