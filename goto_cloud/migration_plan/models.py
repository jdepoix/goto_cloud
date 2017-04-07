from django.contrib.postgres.fields import JSONField

from tracked_model.public import TrackedModel


class MigrationPlan(TrackedModel):
    """
    represents the plan which is used for a migration
    """
    plan = JSONField(default=dict)
