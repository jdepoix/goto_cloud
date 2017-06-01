from unittest import TestCase
from unittest.mock import patch

from test_assets.public import TestAsset

from ..cloud_adapter import ProfitbricksAdapter, CloudAdapter


class TestProfitbricksAdapter(TestCase):
    TEST_SERVER_HOSTNAME = 'test_target'
    TEST_SERVER_RAM = '4096'
    TEST_SERVER_CORES = '2'
    TEST_SERVER_ID = '1'
    TEST_VOLUME_ID = '2'
    TEST_NIC_ID = '3'
    TEST_REQUEST_ID = '4'

    def setUp(self):
        self.adapter = ProfitbricksAdapter(TestAsset.MIGRATION_PLAN_MOCK['target_cloud'])

    @patch(
        'profitbricks.client.ProfitBricksService.get_request',
        return_value={
            'metadata': {
                'status': ProfitbricksAdapter.RequestState.DONE
            }
        }
    )
    @patch('profitbricks.client.ProfitBricksService.create_server', return_value={
        'id': TEST_SERVER_ID,
        'requestId': TEST_REQUEST_ID,
    })
    def test_create_target(self, mocked_create_server, mocked_get_request):
        self.adapter.create_target(self.TEST_SERVER_HOSTNAME, [
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
        ], [5, 8, 30], self.TEST_SERVER_RAM, self.TEST_SERVER_CORES)
        # cant be asserted with assert_called_with, since Server, Volume and NIC don't provide a proper equals method
        self.assertTrue(mocked_create_server.called)
        mocked_get_request.assert_called_with(
            request_id=self.TEST_REQUEST_ID,
            status=True,
        )

    @patch('profitbricks.client.ProfitBricksService.create_server', return_value={
        'id': TEST_SERVER_ID,
        'requestId': TEST_REQUEST_ID,
    })
    @patch.dict(TestAsset.MIGRATION_PLAN_MOCK['target_cloud']['networks'], {'LAN 1': {}})
    def test_create_target__invalid_migration_plan__invalid_network_settings(self, mocked_create_server):
            with self.assertRaises(CloudAdapter.InvalidCloudSettingsException):
                self.adapter.create_target(self.TEST_SERVER_HOSTNAME, [
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
                ], [5, 8, 30], self.TEST_SERVER_RAM, self.TEST_SERVER_CORES)

    @patch('profitbricks.client.ProfitBricksService.create_server', return_value={
        'id': TEST_SERVER_ID,
        'requestId': TEST_REQUEST_ID,
    })
    @patch.dict(TestAsset.MIGRATION_PLAN_MOCK['target_cloud'], {'bootstrapping': {}})
    def test_create_target__invalid_migration_plan__invalid_bootstrapping_settings(self, mocked_create_server):
        with self.assertRaises(CloudAdapter.InvalidCloudSettingsException):
            self.adapter.create_target(self.TEST_SERVER_HOSTNAME, [
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
            ], [5, 8, 30], self.TEST_SERVER_RAM, self.TEST_SERVER_CORES)

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
        with self.assertRaises(ProfitbricksAdapter.CloudConnectionException):
            ProfitbricksAdapter(TestAsset.MIGRATION_PLAN_MOCK['target_cloud'])._wait_for(lambda: False, {}, True, 1, 1)
