from migration_plan.public import MigrationPlan

from migration_run.public import MigrationRun

from .source_parsing import SourceParser
from .db_item_handling import DbItemHandler


class MigrationPlanParser(DbItemHandler):
    def __init__(self):
        super().__init__()

    def parse(self, migration_plan_dict):
        try:
            migration_plan = self._create_migration_plan(migration_plan_dict)
            sources = self._create_sources(migration_plan_dict)

            return self._create_migration_run(migration_plan, sources)
        except Exception as e:
            self.delete()
            raise e

    def _create_migration_plan(self, migration_plan_dict):
        return self.add_db_item(
            MigrationPlan.objects.create(
                plan=migration_plan_dict
            )
        )

    def _create_sources(self, migration_plan_dict):
        source_parser = self.add_db_item(SourceParser(migration_plan_dict['blueprints']))

        return [source_parser.parse(source_dict) for source_dict in migration_plan_dict['sources']]

    def _create_migration_run(self, migration_plan, sources):
        migration_run = self.add_db_item(
            MigrationRun.objects.create(
                plan=migration_plan,
            )
        )

        for source in sources:
            source.migration_run = migration_run
            source.save()

        return migration_run
