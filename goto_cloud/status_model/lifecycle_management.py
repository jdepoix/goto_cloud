class StatusLifecycle():
    """
    This class represents a lifecycle of statuses.
    """
    class InvalidLifecycleException(Exception):
        """
        raised if a lifecycle is invalid
        """
        pass

    def __init__(self, *lifecycle_statuses):
        """
        :param lifecycle_statuses: a set of unique statuses, in the correct order, in which they should reside in this
        lifecycle
        :raises StatusLifecycle.InvalidLifecycleException: if the provided statuses aren't unique
        """
        if len(lifecycle_statuses) < 1:
            raise StatusLifecycle.InvalidLifecycleException('at least one status must be provided')

        if len(lifecycle_statuses) != len(set(lifecycle_statuses)):
            raise StatusLifecycle.InvalidLifecycleException('Lifecycle statuses need to be unique!')

        self.statuses = lifecycle_statuses
        self.index_lookup = {status: index for index, status in enumerate(self.statuses)}


class ObjectStatusLifecycleManager():
    """
    This class manages the StatusLifecycle belonging to a specific object, to be able to provide additional
    functionality, like getting a next of previous status.
    """
    class InvalidStatusException(Exception):
        """
        raise if a status is invalid
        """
        pass

    def __init__(self, status_lifecycle, object_with_status, status_attribute):
        """
        :param status_lifecycle: the StatusLifecycle which should be managed
        :type status_lifecycle: StatusLifecycle
        :param object_with_status: the Object to manage the Lifecycle for
        :type object_with_status: Any
        :param status_attribute: the attribute of the status which contains the current status
        :type status_attribute: str
        """
        self.status_lifecycle = status_lifecycle
        self._object_with_status = object_with_status
        self._status_attribute = status_attribute

    def get_status_by_offset(self, offset, raise_exception=True):
        """
        gets a status by a given offset

        :param offset: the offset
        :type offset: int
        :param raise_exception: if False None will be returned in case the offset points to an invalid status, if True
        an InvalidStatusException will be thrown
        :type raise_exception: bool
        :raises ObjectStatusLifecycleManager.InvalidStatusException: in case raise_exception == True and offset is
        invalid
        :return: the status relative to the provided status, by the given offset
        """
        return self._execute_method_and_handle_index_exceptions(
            raise_exception,
            self._get_status_by_offset,
            offset
        )

    def get_next_status(self, raise_exception=True):
        """
        gets the next status, relative to the given status

        :param raise_exception: if False None will be returned in case there is no next status, if True
        an InvalidStatusException will be thrown
        :type raise_exception: bool
        :raises ObjectStatusLifecycleManager.InvalidStatusException: in case raise_exception == True and offset is
        invalid
        :return: the next status, relative to the given status
        """
        return self._execute_method_and_handle_index_exceptions(
            raise_exception,
            self._get_next_status
        )

    def get_previous_status(self, raise_exception=True):
        """
        gets the previous status, relative to the given status

        :param raise_exception: if False None will be returned in case there is no previous status, if True
        an InvalidStatusException will be thrown
        :type raise_exception: bool
        :raises ObjectStatusLifecycleManager.InvalidStatusException: in case raise_exception == True and offset is
        invalid
        :return: the previous status, relative to the given status
        """
        return self._execute_method_and_handle_index_exceptions(
            raise_exception,
            self._get_previous_status
        )

    def is_status_valid(self, status, raise_exception=False):
        """
        evaluates whether a status is valid or not

        :param status: the status to check
        :type status: str
        :param raise_exception: if True an ObjectStatusLifecycleManager.InvalidStatusException will be raised in case
        the status is invalid
        :type raise_exception: bool
        :raises ObjectStatusLifecycleManager.InvalidStatusException: in case raise_exception == True and invalid
        :return: is the status valid
        :rtype: bool
        """
        valid = status in self.status_lifecycle.statuses
        if not valid and raise_exception:
            raise ObjectStatusLifecycleManager.InvalidStatusException()
        else:
            return valid

    def compare_status_to(self, status_to_compare_to):
        """
        compares the position of current status to another one, to evaluate whether a status is before or after another
        one in the lifecycle.

        :param status_to_compare_to: the status which the current one is compared to
        :type status: str
        :return: returns
            1 -> status > status_to_compare_to
            -1 -> status < status_to_compare_to
            0 -> status == status_to_compare_to
        :rtype int in (-1, 0, 1)
        """
        status_index = self._get_position_of_current_status()
        status_to_compare_to_index = self._get_position_of_status(status_to_compare_to)

        if status_index > status_to_compare_to_index:
            return 1
        if status_index < status_to_compare_to_index:
            return -1
        return 0

    def _get_current_status(self):
        return getattr(self._object_with_status, self._status_attribute)

    def _get_status_by_offset(self, offset):
        index = self._get_position_of_current_status() + offset

        if index < 0:
            raise ObjectStatusLifecycleManager.InvalidStatusException()

        return self.status_lifecycle.statuses[index]

    def _get_next_status(self):
        return self._get_status_by_offset(1)

    def _get_previous_status(self):
        return self._get_status_by_offset(-1)

    def _get_position_of_status(self, status):
        return self.status_lifecycle.index_lookup[status]

    def _get_position_of_current_status(self):
        return self._get_position_of_status(self._get_current_status())

    def _execute_method_and_handle_index_exceptions(self, raise_exception, method, *args):
        try:
            return method(*args)
        except Exception as e:
            if raise_exception:
                raise ObjectStatusLifecycleManager.InvalidStatusException(str(e))
            else:
                return None
