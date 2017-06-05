from unittest import TestCase
from unittest.mock import patch

from test_assets.public import TestAsset

from ..cloud_adapter import CloudAdapter
from ..profitbricks import ProfitbricksAdapter


class TestProfitbricksAdapter(TestCase):
    TEST_SERVER_HOSTNAME = 'test_target'
    TEST_SERVER_RAM = '4096'
    TEST_SERVER_CORES = '2'
    TEST_SERVER_ID = '1'
    TEST_VOLUME_ID = '2'
    TEST_NIC_ID = '3'
    TEST_REQUEST_ID = '4'
    TEST_NETWORK_SETTINGS = [
        {
            'ip': '10.17.32.210',
            'gateway': '10.17.32.1',
            'net_mask': '255.255.255.0',
            'network_id': 'LAN 2',
            'source_interface': 'eth0'
        },
        {
            'ip': None,
            'gateway': None,
            'net_mask': None,
            'network_id': 'LAN 1',
            'source_interface': 'eth1'
        }
    ]
    TEST_PRIVATE_NETWORK_INTERFACE_ID = '5'
    TEST_PUBLIC_NETWORK_INTERFACE_ID = '6'
    TEST_BOOTSTRAP_NETWORK_INTERFACE_ID = '66'
    TEST_VOLUME_IDS = ['7', '8', '9', '10']
    TEST_LIST_NICS_RETURN_VALUE = {
        'items': [
            {
                'id': TEST_PRIVATE_NETWORK_INTERFACE_ID,
                'properties': {
                    'ips': ['10.17.32.210'],
                    'lan': 2,
                    'name': None,
                },
            },
            {
                'id': TEST_PUBLIC_NETWORK_INTERFACE_ID,
                'properties': {
                    'ips': ['8.8.8.8'],
                    'lan': 1,
                    'name': None,
                },
            },
            {
                'id': TEST_BOOTSTRAP_NETWORK_INTERFACE_ID,
                'properties': {
                    'ips': ['9.9.9.9'],
                    'lan': 1,
                    'name': '{hostname}.bootstrap'.format(hostname=TEST_SERVER_HOSTNAME),
                },
            },
        ],
    }
    TEST_LIST_VOLUMES_RETURN_VALUE = {
        'items': [
            {
                'id': TEST_VOLUME_IDS[0],
                'properties': {
                    'deviceNumber': 1,
                    'name': '{hostname}.bootstrap'.format(hostname=TEST_SERVER_HOSTNAME),
                    'size': 10,
                },
            },
            {
                'id': TEST_VOLUME_IDS[1],
                'properties': {
                    'deviceNumber': 2,
                    'name': '{hostname}.clone-0'.format(hostname=TEST_SERVER_HOSTNAME),
                    'size': 5,
                },
            },
            {
                'id': TEST_VOLUME_IDS[2],
                'properties': {
                    'deviceNumber': 3,
                    'name': '{hostname}.clone-1'.format(hostname=TEST_SERVER_HOSTNAME),
                    'size': 8,
                },
            },
            {
                'id': TEST_VOLUME_IDS[3],
                'properties': {
                    'deviceNumber': 4,
                    'name': '{hostname}.clone-2'.format(hostname=TEST_SERVER_HOSTNAME),
                    'size': 30,
                },
            },
        ],
    }


    def setUp(self):
        self.adapter = ProfitbricksAdapter(TestAsset.MIGRATION_PLAN_MOCK['target_cloud'])

    @patch(
        'profitbricks.client.ProfitBricksService.list_nics',
        lambda *args, **kwargs: TestProfitbricksAdapter.TEST_LIST_NICS_RETURN_VALUE
    )
    @patch(
        'profitbricks.client.ProfitBricksService.get_attached_volumes',
        lambda *args, **kwargs: TestProfitbricksAdapter.TEST_LIST_VOLUMES_RETURN_VALUE
    )
    @patch(
        'profitbricks.client.ProfitBricksService.get_request',
        lambda *args, **kwargs: {
            'metadata': {
                'status': ProfitbricksAdapter.RequestState.DONE
            }
        }
    )
    @patch('profitbricks.client.ProfitBricksService.create_server', return_value={
        'id': TEST_SERVER_ID,
        'requestId': TEST_REQUEST_ID,
    })
    def test_create_target__target_created(self, mocked_create_server):
        self.adapter.create_target(
            self.TEST_SERVER_HOSTNAME,
            self.TEST_NETWORK_SETTINGS,
            [5, 8, 30],
            self.TEST_SERVER_RAM,
            self.TEST_SERVER_CORES
        )
        # cant be asserted with assert_called_with, since Server, Volume and NIC don't provide a proper equals method
        self.assertTrue(mocked_create_server.called)

    @patch(
        'profitbricks.client.ProfitBricksService.list_nics',
        lambda *args, **kwargs: TestProfitbricksAdapter.TEST_LIST_NICS_RETURN_VALUE
    )
    @patch(
        'profitbricks.client.ProfitBricksService.get_attached_volumes',
        lambda *args, **kwargs: TestProfitbricksAdapter.TEST_LIST_VOLUMES_RETURN_VALUE
    )
    @patch(
        'profitbricks.client.ProfitBricksService.get_request',
        return_value={
            'metadata': {
                'status': ProfitbricksAdapter.RequestState.DONE
            }
        }
    )
    @patch('profitbricks.client.ProfitBricksService.create_server', lambda *args, **kwargs: {
        'id': TestProfitbricksAdapter.TEST_SERVER_ID,
        'requestId': TestProfitbricksAdapter.TEST_REQUEST_ID,
    })
    def test_create_target__wait_for_request_to_be_done(self, mocked_get_request):
        self.adapter.create_target(
            self.TEST_SERVER_HOSTNAME,
            self.TEST_NETWORK_SETTINGS,
            [5, 8, 30],
            self.TEST_SERVER_RAM,
            self.TEST_SERVER_CORES
        )
        mocked_get_request.assert_called_with(
            request_id=self.TEST_REQUEST_ID,
            status=True,
        )

    @patch('profitbricks.client.ProfitBricksService.list_nics', return_value=TEST_LIST_NICS_RETURN_VALUE)
    @patch('profitbricks.client.ProfitBricksService.get_attached_volumes', return_value=TEST_LIST_VOLUMES_RETURN_VALUE)
    @patch(
        'profitbricks.client.ProfitBricksService.get_request',
        lambda *args, **kwargs: {
            'metadata': {
                'status': ProfitbricksAdapter.RequestState.DONE
            }
        }
    )
    @patch('profitbricks.client.ProfitBricksService.create_server', lambda *args, **kwargs: {
        'id': TestProfitbricksAdapter.TEST_SERVER_ID,
        'requestId': TestProfitbricksAdapter.TEST_REQUEST_ID,
    })
    def test_create_target__created_entities_retrieved(self, mocked_get_attached_volumes, mocked_list_nics):
        self.adapter.create_target(
            self.TEST_SERVER_HOSTNAME,
            self.TEST_NETWORK_SETTINGS,
            [5, 8, 30],
            self.TEST_SERVER_RAM,
            self.TEST_SERVER_CORES
        ),
        mocked_get_attached_volumes.assert_called_with(
            datacenter_id=TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['datacenter'],
            server_id=self.TEST_SERVER_ID
        )
        mocked_list_nics.assert_called_with(
            datacenter_id=TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['datacenter'],
            server_id=self.TEST_SERVER_ID
        )

    @patch(
        'profitbricks.client.ProfitBricksService.list_nics',
        lambda *args, **kwargs: TestProfitbricksAdapter.TEST_LIST_NICS_RETURN_VALUE
    )
    @patch(
        'profitbricks.client.ProfitBricksService.get_attached_volumes',
        lambda *args, **kwargs: TestProfitbricksAdapter.TEST_LIST_VOLUMES_RETURN_VALUE
    )
    @patch(
        'profitbricks.client.ProfitBricksService.get_request',
        lambda *args, **kwargs: {
            'metadata': {
                'status': ProfitbricksAdapter.RequestState.DONE
            }
        }
    )
    @patch('profitbricks.client.ProfitBricksService.create_server', lambda *args, **kwargs: {
        'id': TestProfitbricksAdapter.TEST_SERVER_ID,
        'requestId': TestProfitbricksAdapter.TEST_REQUEST_ID,
    })
    def test_create_target__created_entities_parsed_and_returned(self):
        self.assertDictEqual(
            self.adapter.create_target(
                self.TEST_SERVER_HOSTNAME,
                self.TEST_NETWORK_SETTINGS,
                [5, 8, 30],
                self.TEST_SERVER_RAM,
                self.TEST_SERVER_CORES
            ),
            {
                'id': TestProfitbricksAdapter.TEST_SERVER_ID,
                'volumes': [
                    {
                        'id': TestProfitbricksAdapter.TEST_VOLUME_IDS[0],
                        'size': 10,
                        'device_number': 1,
                        'name': '{hostname}.bootstrap'.format(hostname=TestProfitbricksAdapter.TEST_SERVER_HOSTNAME),
                    },
                    {
                        'id': TestProfitbricksAdapter.TEST_VOLUME_IDS[1],
                        'size': 5,
                        'device_number': 2,
                        'name': '{hostname}.clone-0'.format(hostname=TestProfitbricksAdapter.TEST_SERVER_HOSTNAME),
                    },
                    {
                        'id': TestProfitbricksAdapter.TEST_VOLUME_IDS[2],
                        'size': 8,
                        'device_number': 3,
                        'name': '{hostname}.clone-1'.format(hostname=TestProfitbricksAdapter.TEST_SERVER_HOSTNAME),
                    },
                    {
                        'id': TestProfitbricksAdapter.TEST_VOLUME_IDS[3],
                        'size': 30,
                        'device_number': 4,
                        'name': '{hostname}.clone-2'.format(hostname=TestProfitbricksAdapter.TEST_SERVER_HOSTNAME),
                    },
                ],
                'network_interfaces': [
                    {
                        'id': TestProfitbricksAdapter.TEST_PRIVATE_NETWORK_INTERFACE_ID,
                        'ip': '10.17.32.210',
                        'lan': 2,
                        'name': None,
                    },
                    {
                        'id': TestProfitbricksAdapter.TEST_PUBLIC_NETWORK_INTERFACE_ID,
                        'ip': '8.8.8.8',
                        'lan': 1,
                        'name': None,
                    },
                    {
                        'id': TestProfitbricksAdapter.TEST_BOOTSTRAP_NETWORK_INTERFACE_ID,
                        'ip': '9.9.9.9',
                        'lan': 1,
                        'name': '{hostname}.bootstrap'.format(hostname=TestProfitbricksAdapter.TEST_SERVER_HOSTNAME),
                    },
                ]
            }
        )

    @patch('profitbricks.client.ProfitBricksService.create_server', return_value={
        'id': TEST_SERVER_ID,
        'requestId': TEST_REQUEST_ID,
    })
    @patch.dict(TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['networks'], {'LAN 1': {}})
    def test_create_target__invalid_migration_plan__invalid_network_settings(self, mocked_create_server):
            with self.assertRaises(CloudAdapter.InvalidCloudSettingsException):
                self.adapter.create_target(
                    self.TEST_SERVER_HOSTNAME,
                    self.TEST_NETWORK_SETTINGS,
                    [5, 8, 30],
                    self.TEST_SERVER_RAM,
                    self.TEST_SERVER_CORES
                )

    @patch('profitbricks.client.ProfitBricksService.create_server', return_value={
        'id': TEST_SERVER_ID,
        'requestId': TEST_REQUEST_ID,
    })
    @patch.dict(TestAsset.MIGRATION_PLAN_MOCK['target_cloud'], {'bootstrapping': {}})
    def test_create_target__invalid_migration_plan__invalid_bootstrapping_settings(self, mocked_create_server):
        with self.assertRaises(CloudAdapter.InvalidCloudSettingsException):
            self.adapter.create_target(
                self.TEST_SERVER_HOSTNAME,
                self.TEST_NETWORK_SETTINGS,
                [5, 8, 30],
                self.TEST_SERVER_RAM,
                self.TEST_SERVER_CORES
            )

    @patch(
        'profitbricks.client.ProfitBricksService.get_server',
        return_value={
            'metadata': {
                'state': ProfitbricksAdapter.EntityState.AVAILABLE
            }
        }
    )
    @patch('profitbricks.client.ProfitBricksService.start_server')
    def test_start_target(self, mocked_start_server, mocked_get_server):
        self.adapter.start_target(self.TEST_SERVER_ID)

        mocked_start_server.assert_called_with(
            datacenter_id=TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['datacenter'],
            server_id=self.TEST_SERVER_ID
        )
        mocked_get_server.assert_called_with(
            datacenter_id=TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['datacenter'],
            server_id=self.TEST_SERVER_ID
        )

    @patch(
        'profitbricks.client.ProfitBricksService.get_server',
        return_value={
            'metadata': {
                'state': ProfitbricksAdapter.EntityState.INACTIVE
            }
        }
    )
    @patch('profitbricks.client.ProfitBricksService.stop_server')
    def test_stop_target(self, mocked_stop_server, mocked_get_server):
        self.adapter.stop_target(self.TEST_SERVER_ID)

        mocked_stop_server.assert_called_with(
            datacenter_id=TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['datacenter'],
            server_id=self.TEST_SERVER_ID
        )
        mocked_get_server.assert_called_with(
            datacenter_id=TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['datacenter'],
            server_id=self.TEST_SERVER_ID
        )

    @patch('profitbricks.client.ProfitBricksService.delete_server')
    def test_delete_target(self, mocked_delete_server):
        self.adapter.delete_target(self.TEST_SERVER_ID)

        mocked_delete_server.assert_called_with(
            datacenter_id=TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['datacenter'],
            server_id=self.TEST_SERVER_ID
        )

    @patch('profitbricks.client.ProfitBricksService.delete_volume')
    def test_delete_volume(self, mocked_delete_volume):
        self.adapter.delete_volume(self.TEST_VOLUME_ID)

        mocked_delete_volume.assert_called_with(
            datacenter_id=TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['datacenter'],
            volume_id=self.TEST_VOLUME_ID
        )

    @patch(
        'profitbricks.client.ProfitBricksService.get_server',
        return_value={
            'metadata': {
                'state': ProfitbricksAdapter.EntityState.INACTIVE
            }
        }
    )
    @patch('profitbricks.client.ProfitBricksService.update_server')
    def test_make_volume_boot(self, mocked_update_server, mocked_get_server):
        self.adapter.make_volume_boot(self.TEST_SERVER_ID, self.TEST_VOLUME_ID)

        mocked_update_server.assert_called_with(
            datacenter_id=TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['datacenter'],
            server_id=self.TEST_SERVER_ID,
            boot_volume_id=self.TEST_VOLUME_ID,
        )
        mocked_get_server.assert_called_with(
            datacenter_id=TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['datacenter'],
            server_id=self.TEST_SERVER_ID
        )

    @patch('profitbricks.client.ProfitBricksService.delete_nic')
    def test_delete_nic(self, mocked_delete_nic):
        self.adapter.delete_nic(self.TEST_SERVER_ID, self.TEST_NIC_ID)

        mocked_delete_nic.assert_called_with(
            datacenter_id=TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['datacenter'],
            server_id=self.TEST_SERVER_ID,
            nic_id=self.TEST_NIC_ID,
        )


class TestProfitbricksAdapterPrivate(TestCase):
    @patch('time.sleep', lambda timeout: None)
    def test__wait_for__cloud_connection_exception(self):
        with self.assertRaises(CloudAdapter.CloudConnectionException):
            ProfitbricksAdapter(TestAsset.MIGRATION_PLAN_MOCK['target_cloud'])._wait_for(lambda: False, {}, True, 1, 1)
