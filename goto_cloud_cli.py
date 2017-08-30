#!virtualenv/bin/python

import os
import sys


sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'goto_cloud'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

import django
django.setup()

from profitbricks.errors import PBNotFoundError

from cloud_management.cloud_management import CloudManager

from migration_run.public import MigrationRun

from migration_scheduling.public import MigrationScheduler

from migration_plan_parsing.public import MigrationPlanParser

from tryout_migration_plan import MIGRATION_PLAN

from source.public import Source

from migration_scheduling.tasks import execute_migration


class CliCommand():
    def execute(self, params):
        pass

    def _fail(self, message):
        print(message)
        exit(1)

    def _no_source_id_fail(self):
        self._fail(
            'No source id was provided!\nChoose one of the following sources:\n\n\t{sources}'.format(
                sources='\n\t'.join(
                    '<ID: {source_id} - {source_remote_host_address} - STATUS: {source_status}>'.format(
                        source_id=source.id,
                        source_remote_host_address=source.remote_host.address,
                        source_status=source.status,
                    )
                    for source in Source.objects.exclude(status=Source.Status.LIVE).order_by('-created')
                )
            )
        )


class StartMigration(CliCommand):
    def execute(self, params):
        print('start parsing migration plan...')
        migration_run = MigrationPlanParser().parse(self._load_migration_plan_with_parsed_scripts())
        print('migration plan successfully parsed')
        print('starting migration with id: {migration_run_id}'.format(migration_run_id=migration_run.id))
        MigrationScheduler(migration_run).execute_migration()
        print('finished migration!')
        print(
            'run "./goto_cloud_cli.py golive {migration_run_id}" to go live!'.format(migration_run_id=migration_run.id)
        )

    def _load_script(self, script_name):
        with open('test_scripts/{file_name}'.format(file_name=script_name), 'r') as script_file:
            return script_file.read()

    def _load_migration_plan_with_parsed_scripts(self):
        for blueprint_name, blueprint in MIGRATION_PLAN.get('blueprints', {}).items():
            for lifecycle, hook in blueprint.get('hooks', {}).items():
                if 'script' in hook:
                    MIGRATION_PLAN['blueprints'][blueprint_name]['hooks'][lifecycle]['execute'] = self._load_script(
                        hook['script']
                    )

        return MIGRATION_PLAN


class GoLive(CliCommand):
    def execute(self, params):
        if not params:
            self._fail('no migration run id was provided')

        try:
            migration_run = MigrationRun.objects.get(id=params[0])

            print('starting go live with id: {migration_run_id}'.format(migration_run_id=migration_run.id))

            MigrationScheduler(migration_run).execute_go_live()

            print('finished go live!')
        except MigrationRun.DoesNotExist:
            self._fail('<MigrationRun: {migration_run_id}> could not be found!'.format(migration_run_id=params[0]))


class RestartSourceMigrationStep(CliCommand):
    def execute(self, params):
        if not params:
            self._no_source_id_fail()

        try:
            source = Source.objects.get(id=params[0])

            print('retrying migration of <Source: {source_id}>!'.format(source_id=source.id))

            execute_migration.delay(source.id)
        except Source.DoesNotExist:
            self._fail('<Source: {source_id}> could not be found!'.format(source_id=params[0]))


class SkipSourceMigrationStep(CliCommand):
    def execute(self, params):
        if not params:
            self._no_source_id_fail()

        try:
            source = Source.objects.get(id=params[0])
            source.increment_status()

            print('retrying migration of <Source: {source_id}>!'.format(source_id=source.id))

            execute_migration.delay(source.id)
        except Source.DoesNotExist:
            self._fail('<Source: {source_id}> could not be found!'.format(source_id=params[0]))


class RestartSourceMigration(CliCommand):
    def execute(self, params):
        if not params:
            self._no_source_id_fail()

        try:
            source = Source.objects.get(id=params[0])

            print('deleting previous target system')

            if source.target.remote_host.cloud_metadata:
                cloud_manager = CloudManager(source.migration_run.plan.plan.get('target_cloud', {}))

                for volume in source.target.remote_host.cloud_metadata['volumes']:
                    try:
                        cloud_manager.delete_volume(volume['id'])
                    except PBNotFoundError:
                        pass

                try:
                    cloud_manager.delete_target(source.target.remote_host.cloud_metadata['id'])
                except PBNotFoundError:
                    pass

            target = source.target
            source.target = None
            source.save()
            target.delete()

            source.status = Source.Status.DRAFT
            source.save()

            RestartSourceMigrationStep().execute(params)
        except Source.DoesNotExist:
            self._fail('<Source: {source_id}> could not be found!'.format(source_id=params[0]))


class CliCommandHandler(CliCommand):
    COMMANDS = {
        'migrate': StartMigration,
        'go_live': GoLive,
        'restart_source_migration_step': RestartSourceMigrationStep,
        'skip_source_migration_step': SkipSourceMigrationStep,
        'restart_source_migration': RestartSourceMigration,
    }

    def execute(self, params):
        if not params:
            self._fail('No command provided. Choose one of the following:\n\t{commands}'.format(
                commands='\n\t'.join(self.COMMANDS.keys()))
            )

        command = self.COMMANDS.get(params[0])

        if command:
            command().execute(params[1:])
        else:
            self._fail(
                'Command {command_name} not known. Choose on of the following:\n\t{commands}'.format(
                    command_name=params[0],
                    commands='\n\t'.join(self.COMMANDS.keys())
                )
            )


if __name__ == '__main__':
    CliCommandHandler().execute(sys.argv[1:])
