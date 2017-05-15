import sys

from unittest import TestCase

from target.public import Target

from source.public import Source

from remote_host.public import RemoteHost

from test_assets.public import TestAsset

from system_info_inspection.public import RemoteHostSystemInfoGetter

from ..device_identification import DeviceIdentificationCommand


class TestDeviceIdentificationCommand(TestCase, metaclass=TestAsset.PatchRemoteHostMeta):
    def test_execute(self):
        source_remote_host = RemoteHost.objects.create(address='ubuntu16')
        target_remote_host = RemoteHost.objects.create(address='target__device_identification')

        source_remote_host.system_info = RemoteHostSystemInfoGetter(source_remote_host).get_system_info()
        target_remote_host.system_info = RemoteHostSystemInfoGetter(target_remote_host).get_system_info()

        self.source = Source.objects.create(remote_host=source_remote_host)
        self.target = Target.objects.create(
            source=self.source,
            remote_host=target_remote_host,
        )

        DeviceIdentificationCommand(self.source).execute()

        self.target.refresh_from_db()

        self.assertDictEqual(
            self.target.device_mapping,
            {
                'vda': {
                    'id': 'vdb',
                    'mountpoint': '',
                    'children': {
                        'vda1': {
                            'id': 'vdb1',
                            'mountpoint': '/mnt/' + str(hash('/') + sys.maxsize + 1),
                        }
                    }
                },
                'vdb': {
                    'id': 'vdc',
                    'mountpoint': '',
                    'children': {}
                },
                'vdc': {
                    'id': 'vdd',
                    'mountpoint': '',
                    'children': {
                        'vdc1': {
                            'id': 'vdd1',
                            'mountpoint': '/mnt/' + str(hash('/mnt/vdc1') + sys.maxsize + 1),
                        },
                        'vdc2': {
                            'id': 'vdd2',
                            'mountpoint': '/mnt/' + str(hash('/mnt/vdc2') + sys.maxsize + 1),
                        }
                    }
                },
            }
        )

    def test_execute__not_enough_devices(self):
        source_remote_host = RemoteHost.objects.create(address='ubuntu16')
        target_remote_host = RemoteHost.objects.create(address='target__device_identification')

        source_remote_host.system_info = RemoteHostSystemInfoGetter(source_remote_host).get_system_info()
        target_remote_host.system_info = RemoteHostSystemInfoGetter(target_remote_host).get_system_info()

        source_remote_host.system_info['block_devices']['vdd'] = source_remote_host.system_info['block_devices']['vdc']

        self.source = Source.objects.create(remote_host=source_remote_host)
        self.target = Target.objects.create(
            source=self.source,
            remote_host=target_remote_host,
        )

        with self.assertRaises(DeviceIdentificationCommand.NoMatchingDevicesException):
            DeviceIdentificationCommand(self.source).execute()

    def test_execute__no_matching_device(self):
        source_remote_host = RemoteHost.objects.create(address='ubuntu16')
        target_remote_host = RemoteHost.objects.create(address='target__device_identification')

        source_remote_host.system_info = RemoteHostSystemInfoGetter(source_remote_host).get_system_info()
        target_remote_host.system_info = RemoteHostSystemInfoGetter(target_remote_host).get_system_info()

        source_remote_host.system_info['block_devices']['vdc'] = {
            'type': 'disk',
            'fs': '',
            'uuid': '',
            'label': '',
            'mountpoint': '',
            'size': 5368709120,
            'children': {
                'vdc1': {
                    'type': 'part',
                    'fs': 'ext4',
                    'uuid': 'f52fdfe8-d862-44f9-b9b7-e35c0ada68cf',
                    'label': '',
                    'mountpoint': '',
                    'size': 5368709120,
                    'start': 2048,
                    'end': 10487807,
                    'bootable': False,
                    'children': {},
                },
                'vdc2': {
                    'type': 'part',
                    'fs': '',
                    'uuid': '',
                    'label': '',
                    'mountpoint': '',
                    'size': 5367660544,
                    'start': 10487808,
                    'end': 20971519,
                    'bootable': False,
                    'children': {},
                },
            }
        }

        self.source = Source.objects.create(remote_host=source_remote_host)
        self.target = Target.objects.create(
            source=self.source,
            remote_host=target_remote_host,
        )

        with self.assertRaises(DeviceIdentificationCommand.NoMatchingDevicesException):
            DeviceIdentificationCommand(self.source).execute()

    def test_execute__dont_map_swap_device(self):
        source_remote_host = RemoteHost.objects.create(address='ubuntu12')
        target_remote_host = RemoteHost.objects.create(address='target__device_identification')

        source_remote_host.system_info = RemoteHostSystemInfoGetter(source_remote_host).get_system_info()
        target_remote_host.system_info = RemoteHostSystemInfoGetter(target_remote_host).get_system_info()

        self.source = Source.objects.create(remote_host=source_remote_host)
        self.target = Target.objects.create(
            source=self.source,
            remote_host=target_remote_host,
        )

        DeviceIdentificationCommand(self.source).execute()

        self.target.refresh_from_db()

        self.assertDictEqual(
            self.target.device_mapping,
            {
                'vda': {
                    'id': 'vdb',
                    'mountpoint': '',
                    'children': {
                        'vda1': {
                            'id': 'vdb1',
                            'mountpoint': '/mnt/' + str(hash('/') + sys.maxsize + 1),
                        },
                        'vda2': {
                            'id': 'vdb2',
                            'mountpoint': '',
                        }
                    }
                }
            }
        )
