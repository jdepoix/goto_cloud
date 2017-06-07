from unittest.mock import patch

from django.test import TestCase

from test_assets.public import TestAsset

from migration_plan_parsing.public import MigrationPlanParser

from migration_commander.cloud_control import CreateTargetCommand


class TestCreateTarget(TestCase, metaclass=TestAsset.PatchTrackedRemoteExecutionMeta):
    HOSTNAME = 'ubuntu16'
    CLOUD_DATA = {
        'id': 'ID',
        'volumes': [
            {
                'id': 'ID',
                'size': 10,
                'device_number': 1,
                'name': '{hostname}.bootstrap'.format(hostname=HOSTNAME),
            },
            {
                'id': 'ID',
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
                'id': 'ID',
                'ip': '10.17.34.100',
                'lan': 4,
                'name': None,
            },
            {
                'id': 'ID',
                'ip': '9.9.9.9',
                'lan': 1,
                'name': '{hostname}.bootstrap'.format(hostname=HOSTNAME),
            },
        ]
    }

    def _init_test_data(self):
        # MOCKCEPTION!!!
        with patch.dict(TestAsset.MIGRATION_PLAN_MOCK, {'sources': [{'address': 'ubuntu16', 'blueprint': 'default'}]}):
            self.source = MigrationPlanParser().parse(TestAsset.MIGRATION_PLAN_MOCK).sources.first()

    @patch('cloud_management.public.CloudManager.create_target', return_value=CLOUD_DATA)
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
            [10, 10, 10,],
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
