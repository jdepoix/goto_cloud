from unittest import TestCase
from unittest.mock import patch

from remote_execution.remote_execution import SshRemoteExecutor
from system_info_inspection.system_info_inspection import SystemInfoGetter, DebianSystemInfoGetter

from system_info_inspection.tests.test_vms import UBUNTU_12_04, UBUNTU_16_04, UBUNTU_14_04


def vm_mock_execution_factory(hostname_mapping):
    def execute_vm_mock(remote_executor, command):
        return hostname_mapping.get(remote_executor.hostname).execute(command)

    return execute_vm_mock


DEBIAN_VMS = {
    'ubuntu12VM': UBUNTU_12_04,
    'ubuntu14VM': UBUNTU_14_04,
    'ubuntu16VM': UBUNTU_16_04,
}


# TODO: use public interface
@patch('remote_execution.remote_execution.SshRemoteExecutor.connect', lambda self: None)
@patch('remote_execution.remote_execution.SshRemoteExecutor.close', lambda self: None)
@patch('remote_execution.remote_execution.SshRemoteExecutor.is_connected', lambda self: True)
@patch('remote_execution.remote_execution.SshRemoteExecutor._execute', vm_mock_execution_factory(DEBIAN_VMS))
class TestDebianSystemInfoGetter(TestCase):
    TEST_VMS = DEBIAN_VMS
    TEST_SYSTEM_INFO_GETTER = DebianSystemInfoGetter

    def call_on_all_test_vms(self, call_method, assert_output):
        for hostname in self.TEST_VMS:
            assert_output(
                self.TEST_VMS[hostname],
                call_method(self.TEST_SYSTEM_INFO_GETTER(SshRemoteExecutor(hostname)))
            )

    def test_get_hardware(self):
        self.call_on_all_test_vms(
            lambda system_info_getter: system_info_getter.get_hardware(),
            lambda tested_vm, result: self.assertDictEqual(result, tested_vm.get_config().get('hardware'))
        )

    def test_get_network(self):
        self.call_on_all_test_vms(
            lambda system_info_getter: system_info_getter.get_network_info(),
            lambda tested_vm, result: self.assertDictEqual(result, tested_vm.get_config().get('network'))
        )

    def test_get_os(self):
        self.call_on_all_test_vms(
            lambda system_info_getter: system_info_getter.get_os(),
            lambda tested_vm, result: self.assertDictEqual(result, tested_vm.get_config().get('os'))
        )

    def test_get_block_device(self):
        self.call_on_all_test_vms(
            lambda system_info_getter: system_info_getter.get_block_devices(),
            lambda tested_vm, result: self.assertDictEqual(result, tested_vm.get_config().get('block_devices'))
        )

    def test_get_system_info(self):
        self.call_on_all_test_vms(
            lambda system_info_getter: system_info_getter.get_system_info(),
            lambda tested_vm, result: self.assertDictEqual(result, tested_vm.get_config())
        )
