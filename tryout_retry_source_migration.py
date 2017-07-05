#!virtualenv/bin/python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'goto_cloud'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

import django
django.setup()

from source.public import Source

from migration_scheduling.tasks import execute_migration

if len(sys.argv) < 2:
    print('No source id was provided!')
    print('Choose one of the following sources:')
    print('\n'.join(
        '<ID: {source_id} - {source_remote_host_address} - STATUS: {source_status}>'.format(
            source_id=source.id,
            source_remote_host_address=source.remote_host.address,
            source_status=source.status,
        )
        for source in Source.objects.exclude(status=Source.Status.LIVE).order_by('-created'))
    )
    exit(1)

try:
    source = Source.objects.get(id=sys.argv[1])

    print('retrying migration of <Source: {source_id}>!'.format(source_id=source.id))

    execute_migration.delay(source.id)
except Source.DoesNotExist:
    print('<Source: {source_id}> could not be found!'.format(source_id=sys.argv[1]))
    exit(1)
