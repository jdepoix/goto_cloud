from abc import abstractmethod

from django.db import models

from tracked_model.public import TrackedModel

from .lifecycle_management import ObjectStatusLifecycleManager, StatusLifecycle


class StatusModel(TrackedModel):
    """
    This Model can be inherited by models which have a status in a lifecycle. The property model.lifecycle_manager
    returns a ObjectStatusLifecycleManager containing the relevant lifecycle.
    """
    class InvalidStatusException(Exception):
        """
        raise if a status is invalid
        """
        pass

    @property
    @abstractmethod
    def lifecycle(self):
        """
        :return: the lifecycle of statuses this StatusModel relies on
        :rtype: tuple
        """
        raise NotImplementedError('implement abstractproperty lifecycle!')

    def __init__(self, *args, **kwargs):
        self._status_lifecycle = StatusLifecycle(*self.lifecycle)
        self._lifecycle_manager = ObjectStatusLifecycleManager(self._status_lifecycle, self, 'status')
        self._meta.get_field('status').default = self._status_lifecycle.statuses[0]
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self._lifecycle_manager.is_status_valid(self.status):
            raise StatusModel.InvalidStatusException('status: {status} is not valid'.format(
                status=self.status
            ))

        return super().save(*args, **kwargs)

    status = models.CharField(max_length=255)

    def increment_status(self):
        """
        increments the status of this StatusModel

        :raises: ObjectStatusLifecycleManager.InvalidStatusException in case there is no next status
        """
        self.status = self._lifecycle_manager.get_next_status()
        self.save()

    def decrement_status(self):
        """
        decrements the status of this StatusModel

        :raises: ObjectStatusLifecycleManager.InvalidStatusException in case there is no previous status
        """
        self.status = self._lifecycle_manager.get_previous_status()
        self.save()

    class Meta:
        abstract = True
