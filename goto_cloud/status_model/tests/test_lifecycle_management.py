import unittest

from ..lifecycle_management import ObjectStatusLifecycleManager, StatusLifecycle


class TestStatuses():
    FIRST = 'FIRST'
    SECOND = 'SECOND'
    THIRD = 'THIRD'


class TestStatusObject():
    def __init__(self, status):
        self.status = status


class TestStatusLifecycle(unittest.TestCase):
    def test_init__unique_statuses(self):
        with self.assertRaises(StatusLifecycle.InvalidLifecycleException):
            StatusLifecycle(TestStatuses.FIRST, TestStatuses.SECOND, TestStatuses.THIRD, TestStatuses.FIRST)

    def test_init__at_least_one_status(self):
        with self.assertRaises(StatusLifecycle.InvalidLifecycleException):
            StatusLifecycle()


class TestObjectStatusLifecycleManager(unittest.TestCase):
    def setUp(self):
        self.lifecycle = StatusLifecycle(TestStatuses.FIRST, TestStatuses.SECOND, TestStatuses.THIRD)
        self.status_object = TestStatusObject(TestStatuses.SECOND)
        self.lifecycle_manager = ObjectStatusLifecycleManager(self.lifecycle, self.status_object, 'status')

    def test_get_next_status(self):
        self.assertEqual(self.lifecycle_manager.get_next_status(), TestStatuses.THIRD)

    def test_get_previous_status(self):
        self.assertEqual(self.lifecycle_manager.get_previous_status(), TestStatuses.FIRST)

    def test_get_status_by_offset(self):
        self.status_object.status = TestStatuses.FIRST
        self.assertEqual(self.lifecycle_manager.get_status_by_offset(2), TestStatuses.THIRD)

    def test_get_status_by_offset__none_on_failure(self):
        self.assertEqual(self.lifecycle_manager.get_status_by_offset(10, raise_exception=False), None)

    def test_get_status_by_offset__exception_on_failure__offset_to_big(self):
        with self.assertRaises(ObjectStatusLifecycleManager.InvalidStatusException):
            self.lifecycle_manager.get_status_by_offset(4)

    def test_get_status_by_offset__exception_on_failure__offset_to_small(self):
        with self.assertRaises(ObjectStatusLifecycleManager.InvalidStatusException):
            self.lifecycle_manager.get_status_by_offset(-4)

    def test_is_status_valid(self):
        self.assertEqual(self.lifecycle_manager.is_status_valid(TestStatuses.FIRST), True)

    def test_is_status_valid__not_valid(self):
        self.assertEqual(self.lifecycle_manager.is_status_valid('I_DO_NOT_EXIST'), False)

    def test_is_status_valid__not_valid__raise_exception(self):
        with self.assertRaises(ObjectStatusLifecycleManager.InvalidStatusException):
            self.lifecycle_manager.is_status_valid('I_DO_NOT_EXIST', raise_exception=True)

    def test_compare_status_to__lt(self):
        self.status_object.status = TestStatuses.FIRST
        self.assertEqual(self.lifecycle_manager.compare_status_to(TestStatuses.SECOND), -1)

    def test_compare_status_to__gt(self):
        self.status_object.status = TestStatuses.THIRD
        self.assertEqual(self.lifecycle_manager.compare_status_to(TestStatuses.SECOND), 1)

    def test_compare_status_to__eq(self):
        self.status_object.status = TestStatuses.SECOND
        self.assertEqual(self.lifecycle_manager.compare_status_to(TestStatuses.SECOND), 0)
