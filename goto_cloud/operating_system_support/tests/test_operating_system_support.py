from unittest import TestCase

from ..operating_system_support import OperatingSystemRelations, PartiallySupported


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
    }
}


class PartiallySupportedTestClass(PartiallySupported):
    @property
    def _supported_operating_systems(self):
        return '4', '8'


class TestOperatingSystemRelations(TestCase):
    def setUp(self):
        OperatingSystemRelations._RELATIONS = RELATION_MOCK

    def test_get_subsystems(self):
        self.assertEqual(
            set(OperatingSystemRelations.get_subsystems('2')),
            {'3', '4', '5', '6', '7'}
        )

    def test_get_subsystems__no_subsystems(self):
        self.assertIsNone(OperatingSystemRelations.get_subsystems('11'))

    def test_get_subsystems__no_relations_known(self):
        self.assertIsNone(OperatingSystemRelations.get_subsystems('999'))


class TestPartiallySupported(TestCase):
    def setUp(self):
        OperatingSystemRelations._RELATIONS = RELATION_MOCK

    def test_is_supported(self):
        self.assertTrue(PartiallySupportedTestClass().is_supported('4'))

    def test_is_supported__related(self):
        self.assertTrue(PartiallySupportedTestClass().is_supported('2'))

    def test_is_supported__not_supported(self):
        self.assertFalse(PartiallySupportedTestClass().is_supported('10'))
