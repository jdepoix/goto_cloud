import unittest

from django.test import TestCase

from operating_system.public import OperatingSystem

from remote_host.public import RemoteHost

from ..operating_system_support import OperatingSystemRelations, AbstractedRemoteHostOperator


RELATION_MOCK = {
    '1': {
        '2': {
            '3': {
                '4': '5',
                '6': '7',
            }
        },
        '8': '9',
        '10': '11',
    },
    '12': {
        '13': '14',
        '15': '16',
    }
}


class TestOperationA():
    pass


class TestOperationB():
    pass


class AbstractedRemoteHostOperatorTestImplementation(AbstractedRemoteHostOperator):
    def _get_operating_systems_to_supported_operation_mapping(self):
        return {
            ('2', '8',): TestOperationA,
            ('13',): TestOperationB,
        }

    def _init_operator_class(self, operator_class):
        return operator_class()


class TestOperatingSystemRelations(unittest.TestCase):
    def setUp(self):
        OperatingSystemRelations._RELATIONS = RELATION_MOCK

    def test_get_subsystems(self):
        self.assertEqual(
            set(OperatingSystemRelations('2').get_subsystems()),
            {'3', '4', '5', '6', '7'}
        )

    def test_get_subsystems__no_subsystems(self):
        self.assertEquals(OperatingSystemRelations('11').get_subsystems(), [])

    def test_get_subsystems__no_relations_known(self):
        self.assertEquals(OperatingSystemRelations('999').get_subsystems(), [])

    def test_is_parent_of(self):
        self.assertTrue(OperatingSystemRelations('3').is_parent_of('5'))

    def test_is_child_of(self):
        self.assertTrue(OperatingSystemRelations('3').is_child_of('1'))


class TestAbstractedRemoteHostOperator(TestCase):
    def setUp(self):
        OperatingSystemRelations._RELATIONS = RELATION_MOCK

    def test_initialization(self):
        self.assertTrue(
            isinstance(
                AbstractedRemoteHostOperatorTestImplementation(RemoteHost.objects.create(os='8')).operator,
                TestOperationA
            )
        )
        self.assertTrue(
            isinstance(
                AbstractedRemoteHostOperatorTestImplementation(RemoteHost.objects.create(os='13')).operator,
                TestOperationB
            )
        )

    def test_initialization__related(self):
        self.assertTrue(
            isinstance(
                AbstractedRemoteHostOperatorTestImplementation(RemoteHost.objects.create(os='1')).operator,
                TestOperationA
            )
        )
        self.assertTrue(
            isinstance(
                AbstractedRemoteHostOperatorTestImplementation(RemoteHost.objects.create(os='12')).operator,
                TestOperationB
            )
        )

    def test_initialization__not_supported(self):
        with self.assertRaises(OperatingSystem.NotSupportedException):
            AbstractedRemoteHostOperatorTestImplementation(RemoteHost.objects.create(os='16'))
