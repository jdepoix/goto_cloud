from migration_plan.public import MigrationPlan

from migration_run.public import MigrationRun

from .source_parsing import SourceParser
from .db_item_handling import DbItemHandler


# TODO check availability
class MigrationPlanParser(DbItemHandler):
    """
    Takes care of parsing a migration plan.
    
    It fills the model with the data needed, during the migration, checks that the sources are available and resolves
    the blueprints to determine what the targets are gonna look like
    """
    def __init__(self):
        super().__init__()

    def parse(self, migration_plan_dict):
        """
        parses a given migration plan
        
        :param migration_plan_dict: the migration plan to parse
        :type migration_plan_dict: dict
        :return: the migration run which was created for the given migration plan
        :rtype: MigrationRun
        """
        try:
            migration_plan = self._create_migration_plan(migration_plan_dict)
            sources = self._create_sources(migration_plan_dict)

            return self._create_migration_run(migration_plan, sources)
        except Exception as e:
            self.delete()
            raise e

    def _create_migration_plan(self, migration_plan_dict):
        """
        creates the migration plan db entry
        
        :param migration_plan_dict: the migration plan
        :type: dict
        :return: the created migration plan
        :rtype: MigrationPlan
        """
        return self.add_db_item(
            MigrationPlan.objects.create(
                plan=migration_plan_dict
            )
        )

    def _create_sources(self, migration_plan_dict):
        """
        parses and creates the sources
        
        :param migration_plan_dict: the migration plan
        :type migration_plan_dict: dict
        :return: the created sources
        :rtype: list[source.public.Source]
        """
        source_parser = self.add_db_item(SourceParser(migration_plan_dict['blueprints']))

        return [source_parser.parse(source_dict) for source_dict in migration_plan_dict['sources']]

    def _create_migration_run(self, migration_plan, sources):
        """
        creates the migration run and connects it with the migration plan and sources
        
        :param migration_plan: the migration plan
        :type migration_plan: MigrationPlan
        :param sources: the sources
        :type sources: list[source.public.Source]
        :return: the created migration run
        :rtype: MigrationRun
        """
        migration_run = self.add_db_item(
            MigrationRun.objects.create(
                plan=migration_plan,
            )
        )

        for source in sources:
            source.migration_run = migration_run
            source.save()

        return migration_run
