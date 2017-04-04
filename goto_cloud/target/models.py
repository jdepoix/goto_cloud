from django.db import models
from django.contrib.postgres.fields import JSONField

from migration_run.public import MigrationRun

from tracked_model.public import TrackedModel


class Target(TrackedModel):
    blueprint = JSONField
    migration_run = models.ForeignKey(MigrationRun, related_name='targets')
