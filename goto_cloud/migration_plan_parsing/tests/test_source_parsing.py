from django.test import TestCase

from source.public import Source

from test_assets.public import TestAsset

from ..source_parsing import SourceParser


class TestSourceParsing(TestCase, metaclass=TestAsset.PatchRemoteHostMeta):
    def test_parse__source_created(self):
        source = SourceParser(
            TestAsset.MIGRATION_PLAN_MOCK['blueprints'],
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud'],
        ).parse(TestAsset.MIGRATION_PLAN_MOCK['sources'][0])

        self.assertEquals(Source.objects.first(), source)

    def test_parse__remote_host_created_and_adjusted(self):
        source = SourceParser(
            TestAsset.MIGRATION_PLAN_MOCK['blueprints'],
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud'],
        ).parse(TestAsset.MIGRATION_PLAN_MOCK['sources'][0])

        self.assertEquals(source.remote_host.os, 'Ubuntu')
        self.assertEquals(source.remote_host.version, '12.04')
        self.assertEquals(source.remote_host.address, 'ubuntu12')
        self.assertEquals(source.remote_host.port, 22)
        self.assertEquals(source.remote_host.username, 'root')
        self.assertEquals(source.remote_host.password, 'xxxxxx')
        self.assertEquals(source.remote_host.private_key, 'xxxxx')
        self.assertEquals(source.remote_host.private_key_file_path, '~/.ssh/id_rsa_source')

    def test_parse__target_created(self):
        source = SourceParser(
            TestAsset.MIGRATION_PLAN_MOCK['blueprints'],
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud'],
        ).parse(TestAsset.MIGRATION_PLAN_MOCK['sources'][0])
        self.assertIsNotNone(source.target)

    def test_parse__source_system_info_retrieved(self):
        source = SourceParser(
            TestAsset.MIGRATION_PLAN_MOCK['blueprints'],
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud'],
        ).parse(TestAsset.MIGRATION_PLAN_MOCK['sources'][0])

        self.assertDictEqual(source.remote_host.system_info, TestAsset.REMOTE_HOST_MOCKS['ubuntu12'].get_config())

    def test_parse__target_blueprint_resolved(self):
        source = SourceParser(
            TestAsset.MIGRATION_PLAN_MOCK['blueprints'],
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud'],
        ).parse(TestAsset.MIGRATION_PLAN_MOCK['sources'][0])

        self.assertNotEqual(source.target.blueprint, {})

    def test_parse__network_mapping_removed_from_blueprint(self):
        source = SourceParser(
            TestAsset.MIGRATION_PLAN_MOCK['blueprints'],
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud'],
        ).parse(TestAsset.MIGRATION_PLAN_MOCK['sources'][2])

        self.assertNotIn('network_mapping', source.target.blueprint)

    def test_parse__network_mapped(self):
        source = SourceParser(
            TestAsset.MIGRATION_PLAN_MOCK['blueprints'],
            TestAsset.MIGRATION_PLAN_MOCK['target_cloud'],
        ).parse(TestAsset.MIGRATION_PLAN_MOCK['sources'][0])

        self.assertIn('network_interfaces', source.target.blueprint)

    def test_parse__no_blueprint(self):
        with self.assertRaises(SourceParser.InvalidSourceException):
            SourceParser(
                TestAsset.MIGRATION_PLAN_MOCK['blueprints'],
                TestAsset.MIGRATION_PLAN_MOCK['target_cloud'],
            ).parse({
                "address": "ubuntu12",
            })
