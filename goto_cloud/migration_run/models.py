from django.db import models

from tracked_model.public import TrackedModel

from migration_plan.public import MigrationPlan


class MigrationRun(TrackedModel):
    """
    represents a single execution of migration, defined by the migration plan, this run is related to
    """
    plan = models.ForeignKey(MigrationPlan, related_name='migration_runs')
