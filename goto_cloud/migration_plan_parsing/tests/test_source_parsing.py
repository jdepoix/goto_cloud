from unittest.mock import patch

from django.test import TestCase

from remote_host_mocks.public import UBUNTU_16_04, UBUNTU_14_04, UBUNTU_12_04

from source.public import Source

from ..source_parsing import SourceParser

from .assets.migration_plan_mock import MIGRATION_PLAN_MOCK


def vm_mock_execution_factory(hostname_mapping):
    def execute_vm_mock(remote_executor, command):
        return hostname_mapping.get(remote_executor.hostname).execute(command)

    return execute_vm_mock


DEBIAN_VMS = {
    'ubuntu12VM': UBUNTU_12_04,
    'ubuntu14VM': UBUNTU_14_04,
    'ubuntu16VM': UBUNTU_16_04,
}


@patch('remote_execution.remote_execution.SshRemoteExecutor.connect', lambda self: None)
@patch('remote_execution.remote_execution.SshRemoteExecutor.close', lambda self: None)
@patch('remote_execution.remote_execution.SshRemoteExecutor.is_connected', lambda self: True)
@patch('remote_execution.remote_execution.SshRemoteExecutor._execute', vm_mock_execution_factory(DEBIAN_VMS))
class TestSourceParsing(TestCase):
    def test_parse(self):
        source = SourceParser(MIGRATION_PLAN_MOCK['blueprints']).parse(MIGRATION_PLAN_MOCK['sources'][0])

        self.assertEquals(Source.objects.first(), source)

        self.assertEquals(source.remote_host.os, 'Ubuntu')
        self.assertEquals(source.remote_host.version, '12.04')
        self.assertEquals(source.remote_host.address, 'ubuntu12VM')
        self.assertEquals(source.remote_host.port, 22)
        self.assertEquals(source.remote_host.username, 'root')
        self.assertEquals(source.remote_host.password, 'xxxxxx')
        self.assertEquals(source.remote_host.private_key, 'xxxxx')
        self.assertEquals(source.remote_host.private_key_file_path, '~/.ssh/id_rsa_source')
        self.assertIsNotNone(source.target)

        self.assertDictEqual(source.remote_host.system_info, UBUNTU_12_04.get_config())

    def test_parse__no_blueprint(self):
        with self.assertRaises(SourceParser.InvalidSourceException):
            SourceParser(MIGRATION_PLAN_MOCK['blueprints']).parse({
                "address": "ubuntu12VM",
            })
