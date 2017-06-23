#!virtualenv/bin/python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'goto_cloud'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

import django
django.setup()

from migration_run.public import MigrationRun
from migration_scheduling.public import MigrationScheduler

if len(sys.argv) < 2:
    print('no migration run id was provided')
    exit(0)

migration_run = MigrationRun.objects.get(id=sys.argv[1])

print('starting go live with id: {migration_run_id}'.format(migration_run_id=migration_run.id))

MigrationScheduler(migration_run).execute_go_live()

print('finished go live!')