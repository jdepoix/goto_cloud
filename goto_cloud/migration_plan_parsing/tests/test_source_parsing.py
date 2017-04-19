from django.test import TestCase

from remote_host_mocks.public import PatchRemoteHostMeta

from source.public import Source

from ..source_parsing import SourceParser

from .assets.migration_plan_mock import MIGRATION_PLAN_MOCK


class TestSourceParsing(TestCase, metaclass=PatchRemoteHostMeta):
    def test_parse(self):
        source = SourceParser(MIGRATION_PLAN_MOCK['blueprints']).parse(MIGRATION_PLAN_MOCK['sources'][0])

        self.assertEquals(Source.objects.first(), source)

        self.assertEquals(source.remote_host.os, 'Ubuntu')
        self.assertEquals(source.remote_host.version, '12.04')
        self.assertEquals(source.remote_host.address, 'ubuntu12')
        self.assertEquals(source.remote_host.port, 22)
        self.assertEquals(source.remote_host.username, 'root')
        self.assertEquals(source.remote_host.password, 'xxxxxx')
        self.assertEquals(source.remote_host.private_key, 'xxxxx')
        self.assertEquals(source.remote_host.private_key_file_path, '~/.ssh/id_rsa_source')
        self.assertIsNotNone(source.target)

        self.assertDictEqual(source.remote_host.system_info, PatchRemoteHostMeta.MOCKS['ubuntu12'].get_config())

    def test_parse__no_blueprint(self):
        with self.assertRaises(SourceParser.InvalidSourceException):
            SourceParser(MIGRATION_PLAN_MOCK['blueprints']).parse({
                "address": "ubuntu12",
            })
