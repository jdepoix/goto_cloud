from ..source_file_location_resolving import SourceFileLocationResolver

from .utils import MigrationCommanderTestCase


class TestSourceFileLocationResolver(MigrationCommanderTestCase):
    def _init_test_data(self, source_host, target_host):
        super()._init_test_data(source_host, target_host)
        self.resolver = SourceFileLocationResolver(self.source)

    def test_resolve_path__root_path(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.assertEqual(
            self.resolver.resolve_path('/etc/fstab'),
            self.source.target.device_mapping['vda']['children']['vda1']['mountpoint'] + '/etc/fstab'
        )

    def test_resolve_path__nested_path(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.assertEqual(
            self.resolver.resolve_path('/mnt/vdc2/test/path/file'),
            self.source.target.device_mapping['vdc']['children']['vdc2']['mountpoint'] + '/test/path/file'
        )

    def test_resolve_path__trailing_slash(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.assertEqual(
            self.resolver.resolve_path('/mnt/vdc2/test/path/file/'),
            self.source.target.device_mapping['vdc']['children']['vdc2']['mountpoint'] + '/test/path/file/'
        )

    def test_resolve_path__root(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.assertEqual(
            self.resolver.resolve_path('/'),
            self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
        )

    def test_resolve_path__device_mountpoint(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.source.remote_host.system_info['block_devices']['vdb']['mountpoint'] = '/var'
        self.source.remote_host.save()
        self.source.target.device_mapping['vdb']['mountpoint'] = '/mnt/test'
        self.source.target.save()

        self.assertEqual(
            self.resolver.resolve_path('/var'),
            self.source.target.device_mapping['vdb']['mountpoint']
        )

    def test_resolve_path__fail_on_relative_path(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        with self.assertRaises(SourceFileLocationResolver.InvalidPathException):
            self.resolver.resolve_path('relative/path')

    def test_resolve_path__fail_no_root_mountpoint(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.source.remote_host.system_info['block_devices']['vda']['children']['vda1']['mountpoint'] = ''
        self.source.remote_host.save()

        with self.assertRaises(SourceFileLocationResolver.InvalidPathException):
            self.resolver.resolve_path('/etc')

    def test_resolve_device(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.assertEqual(
            self.resolver.resolve_device('/boot'),
            'vdb1'
        )

    def test_resolve_disk(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.assertEqual(
            self.resolver.resolve_disk('/boot'),
            'vdb'
        )

    def test_resolve_disk__with_mountpoint_on_disk(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.source.remote_host.system_info['block_devices']['vdb']['mountpoint'] = '/var'
        self.source.remote_host.save()
        self.source.target.device_mapping['vdb'] = {
            'id': 'vdc',
            'mountpoint': '/mnt/test',
            'children': {}
        }
        self.source.target.save()

        self.assertEqual(
            self.resolver.resolve_disk('/var'),
            'vdc'
        )
