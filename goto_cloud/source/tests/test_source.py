from unittest.mock import patch

from django.test import TestCase

from source.public import Source

from remote_host.public import RemoteHost


TEST_LIFECYCLE = (
    'FIRST',
    'SECOND',
    'THIRD',
)


class TestSource(TestCase):
    @patch('source.models.Source._LIFECYCLE', TEST_LIFECYCLE)
    def setUp(self):
        self.test_source = Source.objects.create(remote_host=RemoteHost.objects.create())

    def test_init__default_value(self):
        self.assertEquals(self.test_source.status, 'FIRST')

    def test_init__choices(self):
        with self.assertRaises(Source.InvalidStatusException):
            Source.objects.create(remote_host=RemoteHost.objects.create(), status='status_does_not_exist')

    def test_increment_status(self):
        self.assertEquals(self.test_source.status, 'FIRST')
        self.test_source.increment_status()
        self.assertEquals(self.test_source.status, 'SECOND')

    def test_decrement_status(self):
        self.test_source.status = 'SECOND'
        self.test_source.save()

        self.assertEquals(self.test_source.status, 'SECOND')
        self.test_source.decrement_status()
        self.assertEquals(self.test_source.status, 'FIRST')
