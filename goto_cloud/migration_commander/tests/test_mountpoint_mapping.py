import sys

from unittest import TestCase

from ..mountpoint_mapping import MountpointMapper


class TestMountpointTester(TestCase):
    def test_map_mountpoint(self):
        self.assertEqual(
            MountpointMapper.map_mountpoint('/mnt', '/'),
            '/mnt/' + str(hash('/') + sys.maxsize + 1)
        )

    def test_map_mountpoint__trailing_slash(self):
        self.assertEqual(
            MountpointMapper.map_mountpoint('/mnt/', '/'),
            '/mnt/' + str(hash('/') + sys.maxsize + 1)
        )

    def test_map_mountpoint__no_parent_directory(self):
        self.assertEqual(
            MountpointMapper.map_mountpoint('', '/'),
            str(hash('/') + sys.maxsize + 1)
        )
