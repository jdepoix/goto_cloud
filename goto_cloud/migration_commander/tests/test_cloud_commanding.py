from unittest.mock import patch

from django.test import TestCase

from test_assets.public import TestAsset

from migration_plan_parsing.public import MigrationPlanParser

from source.public import Source

from remote_host.public import RemoteHost

from ..cloud_commanding import \
    CreateTargetCommand, \
    DeleteBootstrapNetworkInterfaceCommand,\
    DeleteBootstrapVolumeCommand, \
    ConfigureBootDeviceCommand, \
    StopTargetCommand, \
    StartTargetCommand
from ..device_identification import DeviceIdentificationCommand
from ..target_system_info_inspection import GetTargetSystemInfoCommand


class CloudCommandTestCase(TestCase, metaclass=TestAsset.PatchTrackedRemoteExecutionMeta):
    HOSTNAME = 'ubuntu16'
    BOOTSTRAP_VOLUME_ID = 'BOOTSTRAP_VOLUME_ID'
    BOOTSTRAP_INTERFACE_ID = 'BOOTSTRAP_INTERFACE_ID'
    NEW_BOOT_VOLUME_ID = 'NEW_BOOT_VOLUME_ID'
    CLOUD_DATA = {
        'id': 'ID',
        'volumes': [
            {
                'id': BOOTSTRAP_VOLUME_ID,
                'size': 10,
                'device_number': 1,
                'name': '{hostname}.bootstrap'.format(hostname=HOSTNAME),
            },
            {
                'id': NEW_BOOT_VOLUME_ID,
                'size': 10,
                'device_number': 2,
                'name': '{hostname}.clone-0'.format(hostname=HOSTNAME),
            },
            {
                'id': 'ID',
                'size': 10,
                'device_number': 3,
                'name': '{hostname}.clone-1'.format(hostname=HOSTNAME),
            },
            {
                'id': 'ID',
                'size': 10,
                'device_number': 4,
                'name': '{hostname}.clone-2'.format(hostname=HOSTNAME),
            },
        ],
        'network_interfaces': [
            {
                'id': BOOTSTRAP_INTERFACE_ID,
                'ip': '10.17.32.50',
                'lan': 2,
                'name': '{hostname}.bootstrap'.format(hostname=HOSTNAME),
            },
            {
                'id': 'ID',
                'ip': '10.17.34.100',
                'lan': 4,
                'name': None,
            },
        ]
    }

    def _init_test_data(self):
        # MOCKCEPTION!!!
        with patch.dict(TestAsset.MIGRATION_PLAN_MOCK, {'sources': [{'address': 'ubuntu16', 'blueprint': 'default'}]}):
            self.source = MigrationPlanParser().parse(TestAsset.MIGRATION_PLAN_MOCK).sources.first()


class TestCreateTarget(CloudCommandTestCase):
    @patch('cloud_management.public.CloudManager.create_target', return_value=CloudCommandTestCase.CLOUD_DATA)
    def test_execute__create_target_executed(self, mocked_create_target):
        self._init_test_data()
        CreateTargetCommand(self.source).execute()

        mocked_create_target.assert_called_with(
            TestCreateTarget.HOSTNAME,
            {
                'ip': '10.17.32.50',
                'gateway': '10.17.32.1',
                'net_mask': '255.255.255.0',
                'network_id': 'LAN 2',
            },
            [
                {
                    'ip': '10.17.34.100',
                    'gateway': '10.17.34.1',
                    'net_mask': '255.255.255.0',
                    'network_id': 'LAN 4',
                    'source_interface': 'eth0',
                },
            ],
            [10, 10, 10, ],
            1024,
            1,
        )

    @patch(
        'cloud_management.public.CloudManager.create_target',
        lambda *args, **kwargs: TestCreateTarget.CLOUD_DATA
    )
    def test_execute__target_remote_host_created(self):
        self._init_test_data()
        CreateTargetCommand(self.source).execute()

        self.assertIsNotNone(self.source.target.remote_host)

    @patch(
        'cloud_management.public.CloudManager.create_target',
        lambda *args, **kwargs: TestCreateTarget.CLOUD_DATA
    )
    def test_execute__target_remote_host_cloud_data_set(self):
        self._init_test_data()
        CreateTargetCommand(self.source).execute()

        self.assertEquals(self.source.target.remote_host.cloud_metadata, TestCreateTarget.CLOUD_DATA)

    @patch(
        'cloud_management.public.CloudManager.create_target',
        lambda *args, **kwargs: TestCreateTarget.CLOUD_DATA
    )
    def test_execute__target_remote_host_ip_set(self):
        self._init_test_data()
        CreateTargetCommand(self.source).execute()

        self.assertEquals(
            self.source.target.remote_host.address,
            next(
                network_interface['ip']
                for network_interface in TestCreateTarget.CLOUD_DATA['network_interfaces']
                if network_interface['name'] and '.bootstrap' in network_interface['name']
            )
        )

    @patch(
        'cloud_management.public.CloudManager.create_target',
        lambda *args, **kwargs: TestCreateTarget.CLOUD_DATA
    )
    def test_execute__target_remote_host_credentials_set(self):
        self._init_test_data()
        CreateTargetCommand(self.source).execute()

        self.assertEquals(
            self.source.target.remote_host.private_key,
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['bootstrapping']['ssh']['private_key']
        )
        self.assertEquals(
            self.source.target.remote_host.private_key_file_path,
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['bootstrapping']['ssh']['private_key_file_path']
        )
        self.assertEquals(
            self.source.target.remote_host.username,
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['bootstrapping']['ssh']['username']
        )
        self.assertEquals(
            self.source.target.remote_host.password,
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['bootstrapping']['ssh']['password']
        )
        self.assertEquals(
            self.source.target.remote_host.port,
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['bootstrapping']['ssh']['port']
        )


class AfterCreationCoudCommandTestCase(CloudCommandTestCase):
    @patch('cloud_management.public.CloudManager.create_target', lambda *args, **kwargs: TestCreateTarget.CLOUD_DATA)
    def _init_test_data(self):
        super()._init_test_data()
        CreateTargetCommand(self.source).execute()


class TestStopTargetCommand(AfterCreationCoudCommandTestCase):
    @patch('cloud_management.public.CloudManager.stop_target')
    def test_execute(self, mocked_stop_target):
        self._init_test_data()
        StopTargetCommand(self.source).execute()

        mocked_stop_target.assert_called_with(self.CLOUD_DATA['id'])


class TestDeleteBootstrapVolumeCommand(AfterCreationCoudCommandTestCase):
    @patch('cloud_management.public.CloudManager.delete_volume')
    def test_execute(self, mocked_delete_volume):
        self._init_test_data()
        DeleteBootstrapVolumeCommand(self.source).execute()

        mocked_delete_volume.assert_called_with(self.BOOTSTRAP_VOLUME_ID)

    def test_execute__no_bootstrapping_volume_found(self):
        self._init_test_data()
        self.source.target.remote_host.refresh_from_db()
        self.source.target.remote_host.cloud_metadata['volumes'].pop(0)
        self.source.target.remote_host.save()

        with self.assertRaises(DeleteBootstrapVolumeCommand.NoBootstrapVolumeFoundException):
            DeleteBootstrapVolumeCommand(self.source).execute()


class TestDeleteBootstrapNetworkInterfaceCommand(AfterCreationCoudCommandTestCase):
    @patch('cloud_management.public.CloudManager.delete_nic')
    def test_execute(self, mocked_delete_nic):
        self._init_test_data()
        DeleteBootstrapNetworkInterfaceCommand(self.source).execute()

        mocked_delete_nic.assert_called_with(self.CLOUD_DATA['id'], self.BOOTSTRAP_INTERFACE_ID)

    def test_execute__no_bootstrapping_interface_found(self):
        self._init_test_data()
        self.source.target.remote_host.refresh_from_db()
        self.source.target.remote_host.cloud_metadata['network_interfaces'].pop(0)
        self.source.target.remote_host.save()

        with self.assertRaises(DeleteBootstrapNetworkInterfaceCommand.NoBootstrapNetworkInterfaceFoundException):
            DeleteBootstrapNetworkInterfaceCommand(self.source).execute()


class TestConfigureBootDeviceCommand(AfterCreationCoudCommandTestCase):
    @patch('cloud_management.public.CloudManager.create_target', lambda *args, **kwargs: TestCreateTarget.CLOUD_DATA)
    def _init_test_data(self):
        super()._init_test_data()

        self.source = Source.objects.get(remote_host__address='ubuntu16')
        self.source.target.remote_host = RemoteHost.objects.create(address='target__device_identification')
        self.source.target.save()

        GetTargetSystemInfoCommand(self.source).execute()
        DeviceIdentificationCommand(self.source).execute()
        CreateTargetCommand(self.source).execute()

    @patch('cloud_management.public.CloudManager.make_volume_boot')
    def test_execute(self, mocked_make_volume_boot):
        self._init_test_data()
        ConfigureBootDeviceCommand(self.source).execute()

        mocked_make_volume_boot.assert_called_with(self.CLOUD_DATA['id'], self.NEW_BOOT_VOLUME_ID)


class TestStartTargetCommand(AfterCreationCoudCommandTestCase):
    @patch('cloud_management.public.CloudManager.start_target')
    def test_execute(self, mocked_start_target):
        self._init_test_data()
        StartTargetCommand(self.source).execute()

        mocked_start_target.assert_called_with(self.CLOUD_DATA['id'])
