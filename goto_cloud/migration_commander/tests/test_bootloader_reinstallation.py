from ..bootloader_reinstallation import BootloaderReinstallation

from .utils import MigrationCommanderTestCase


class TestBootloaderReinstallation(MigrationCommanderTestCase):
    def test_execute__proc_mount_dir_created(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallation(self.source).execute()

        self.assertIn(
            'sudo mkdir {mounted_root}/proc'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
             ),
            self.executed_commands
        )

    def test_execute__sys_mount_dir_created(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallation(self.source).execute()

        self.assertIn(
            'sudo mkdir {mounted_root}/sys'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
             ),
            self.executed_commands
        )

    def test_execute__dev_mount_dir_created(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallation(self.source).execute()

        self.assertIn(
            'sudo mkdir {mounted_root}/dev'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
             ),
            self.executed_commands
        )

    def test_execute__proc_mounted(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallation(self.source).execute()

        self.assertIn(
            'sudo mount -t proc proc {mounted_root}/proc/'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
             ),
            self.executed_commands
        )

    def test_execute__sys_mounted(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallation(self.source).execute()

        self.assertIn(
            'sudo mount -t sysfs sys {mounted_root}/sys/'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
            ),
            self.executed_commands
        )

    def test_execute__dev_mounted(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallation(self.source).execute()

        self.assertIn(
            'sudo mount -o bind /dev {mounted_root}/dev/'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
            ),
            self.executed_commands
        )

    def test_execute__chrooted_into_mounted_root_and_install_bootloader(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallation(self.source).execute()

        self.assertIn(
            'sudo chroot {mounted_root} sudo grub-install --boot-directory=/boot /dev/{mounted_root_device_id}'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint'],
                mounted_root_device_id=self.source.target.device_mapping['vda']['id'],
            ),
            self.executed_commands
        )

    def test_execute__chrooted_into_mounted_root_and_install_bootloader_with_root_mountpoint_on_disk(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.source.target.device_mapping['vda']['mountpoint'] = \
            self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
        self.source.target.save()

        BootloaderReinstallation(self.source).execute()

        self.assertIn(
            'sudo chroot {mounted_root} sudo grub-install --boot-directory=/boot /dev/{mounted_root_device_id}'.format(
                mounted_root=self.source.target.device_mapping['vda']['mountpoint'],
                mounted_root_device_id=self.source.target.device_mapping['vda']['id'],
            ),
            self.executed_commands
        )
