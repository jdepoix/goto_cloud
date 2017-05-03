from ..source_file_location_resolving import SourceFileLocationResolver

from .utils import MigrationCommanderTestCase


class TestSourceFileLocationResolver(MigrationCommanderTestCase):
    def _init_test_data(self, source_host, target_host):
        super()._init_test_data(source_host, target_host)
        self.resolver = SourceFileLocationResolver(self.source)

    def test_resolve__root_path(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.assertEqual(
            self.resolver.resolve('/etc/fstab'),
            self.source.target.device_mapping['vda']['children']['vda1']['mountpoint'] + '/etc/fstab'
        )

    def test_resolve__nested_path(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.assertEqual(
            self.resolver.resolve('/mnt/vdc2/test/path/file'),
            self.source.target.device_mapping['vdc']['children']['vdc2']['mountpoint'] + '/test/path/file'
        )

    def test_resolve__fail_on_relative_path(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        with self.assertRaises(SourceFileLocationResolver.InvalidPathException):
            self.resolver.resolve('relative/path')

    def test_resolve__fail_no_root_mountpoint(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.source.remote_host.system_info['block_devices']['vda']['children']['vda1']['mountpoint'] = ''
        self.source.remote_host.save()

        with self.assertRaises(SourceFileLocationResolver.InvalidPathException):
            self.resolver.resolve('/etc')
