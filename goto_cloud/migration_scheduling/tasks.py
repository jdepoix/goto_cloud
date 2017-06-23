from settings.celery import app

from source.public import Source

from migration_commander.public import MigrationCommander


@app.task()
def execute_migration(source_id):
    MigrationCommander(Source.objects.get(id=source_id)).execute()

@app.task()
def increment_status_and_execute_migration(source_id):
    MigrationCommander(Source.objects.get(id=source_id)).increment_status_and_execute()
