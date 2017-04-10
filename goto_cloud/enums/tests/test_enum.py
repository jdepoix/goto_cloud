from unittest import TestCase

from ..enums import StringEnum


class EnumMock(StringEnum):
    STATUS_ONE = 'status_one'
    STATUS_TWO = 'status_two'
    STATUS_THREE = 'status_three'


class TestStringEnum(TestCase):
    def test_get_django_choices(self):
        self.assertEquals(
            EnumMock.get_django_choices(),
            (
                ('STATUS_ONE', EnumMock.STATUS_ONE),
                ('STATUS_THREE', EnumMock.STATUS_THREE),
                ('STATUS_TWO', EnumMock.STATUS_TWO),
            ),
        )
