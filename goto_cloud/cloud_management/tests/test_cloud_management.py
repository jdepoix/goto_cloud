from test_assets.public import TestAsset

from ..cloud_management import CloudManager, CloudProvider

from .test_profitbricks import TestProfitbricksAdapter


class TestCloudManager(TestProfitbricksAdapter):
    def setUp(self):
        self.adapter = CloudManager(TestAsset.MIGRATION_PLAN_MOCK['target_cloud'])

    def test_invalid_cloud_settings(self):
        with self.assertRaises(CloudManager.InvalidCloudSettingsException):
            CloudManager({})

    def test_unsupported_cloud_provider(self):
        with self.assertRaises(CloudProvider.UnsupportedProviderException):
            CloudManager({'provider': 'NOT_SUPPORTED'})
