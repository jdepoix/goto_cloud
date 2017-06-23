#!virtualenv/bin/python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'goto_cloud'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

import django
django.setup()

from migration_plan_parsing.public import MigrationPlanParser
from migration_scheduling.public import MigrationScheduler
from tryout_migration_plan import MIGRATION_PLAN


def load_script(script_name):
    with open('test_scripts/{file_name}'.format(file_name=script_name), 'r') as script_file:
        return script_file.read()


def load_migration_plan_with_parsed_scripts():
    for blueprint_name, blueprint in MIGRATION_PLAN.get('blueprints', {}).items():
        for lifecycle, hook in blueprint.get('hooks', {}).items():
            if 'script' in hook:
                MIGRATION_PLAN['blueprints'][blueprint_name]['hooks'][lifecycle]['execute'] = load_script(
                    hook['script']
                )

    return MIGRATION_PLAN

print('start parsing migration plan...')
migration_run = MigrationPlanParser().parse(load_migration_plan_with_parsed_scripts())
print('migration plan successfully parsed')
print('starting migration with id: {migration_run_id}'.format(migration_run_id=migration_run.id))
MigrationScheduler(migration_run).execute_migration()
print('finished migration!')
print('run "./tryout_go_live.py {migration_run_id}" to go live!'.format(migration_run_id=migration_run.id))
