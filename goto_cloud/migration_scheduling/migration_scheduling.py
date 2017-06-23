import time

from source.public import Source

from .tasks import execute_migration, increment_status_and_execute_migration


class MigrationScheduler():
    def __init__(self, migration_run):
        """
        :param migration_run: the migration run to execute
        :type migration_run: migration_run.public.MigrationRun
        """
        self._migration_run = migration_run

    def execute_migration(self):
        self._execute_migration_task_on_sources(
            execute_migration,
            self._migration_run.sources.filter(status=Source.Status.DRAFT)
        )

    def execute_go_live(self):
        self._execute_migration_task_on_sources(
            increment_status_and_execute_migration,
            self._migration_run.sources.filter(status=Source.Status.SYNC)
        )

    def _execute_migration_task_on_sources(self, migration_task, sources_to_migrate):
        sources_to_migrate_list = list(sources_to_migrate)
        running_tasks = []

        while sources_to_migrate_list or running_tasks:
            while (
                sources_to_migrate_list
                and len(running_tasks) < self._migration_run.plan.plan['migration']['simultaneous_migrations']
            ):
                source_to_migrate = sources_to_migrate_list.pop(0)
                print('Start migrating {source_address}...'.format(
                    source_address=source_to_migrate.remote_host.address)
                )
                running_tasks.append(migration_task.delay(source_to_migrate.id))

            time.sleep(20)

            for task in running_tasks:
                if task.status == 'SUCCESS':
                    running_tasks.pop()
