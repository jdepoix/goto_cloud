from ..device_modification import DeviceModifyingCommand

from .utils import MigrationCommanderTestCase


class TestDeviceModifyingCommand(DeviceModifyingCommand):
    def _execute(self):
        pass

    def execute_with_swap_included(self):
        self.executed_on_device = []
        self._execute_on_every_device(self._execute_on_disk, self._execute_on_partition, True)

    def execute_without_swap(self):
        self.executed_on_device = []
        self._execute_on_every_device(self._execute_on_disk, self._execute_on_partition)

    def _execute_on_disk(self, remote_executor, source_device, target_device):
        self.executed_on_device.append(source_device[0])

    def _execute_on_partition(
        self, remote_executor, source_device, target_device, partition_device, target_partition_device
    ):
        self.executed_on_device.append(partition_device[0])


class TestDeviceModification(MigrationCommanderTestCase):
    def test_execute_on_every_disk__exclude_swap(self):
        self._init_test_data('ubuntu12', 'target__device_identification')

        self.source.remote_host.system_info['block_devices']['vda']['fs'] = 'swap'
        self.source.remote_host.save()

        device_modifying_command = TestDeviceModifyingCommand(self.source)
        device_modifying_command.execute_without_swap()

        self.assertNotIn('vda', device_modifying_command.executed_on_device)

    def test_execute_on_every_disk__include_swap(self):
        self._init_test_data('ubuntu12', 'target__device_identification')

        self.source.remote_host.system_info['block_devices']['vda']['fs'] = 'swap'
        self.source.remote_host.save()

        device_modifying_command = TestDeviceModifyingCommand(self.source)
        device_modifying_command.execute_with_swap_included()

        self.assertIn('vda', device_modifying_command.executed_on_device)

    def test_execute_on_every_partition__exclude_swap(self):
        self._init_test_data('ubuntu12', 'target__device_identification')

        device_modifying_command = TestDeviceModifyingCommand(self.source)
        device_modifying_command.execute_without_swap()

        self.assertIn('vda1', device_modifying_command.executed_on_device)
        self.assertNotIn('vda2', device_modifying_command.executed_on_device)

    def test_execute_on_every_partition__include_swap(self):
        self._init_test_data('ubuntu12', 'target__device_identification')

        device_modifying_command = TestDeviceModifyingCommand(self.source)
        device_modifying_command.execute_with_swap_included()

        self.assertIn('vda1', device_modifying_command.executed_on_device)
        self.assertIn('vda2', device_modifying_command.executed_on_device)
