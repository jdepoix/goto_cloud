from ..bootloader_reinstallation import BootloaderReinstallationCommand

from .utils import MigrationCommanderTestCase


class TestBootloaderReinstallation(MigrationCommanderTestCase):
    def test_execute__env_mount_dirs_created(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallationCommand(self.source).execute()

        self.assertIn(
            'sudo mkdir -p {mounted_root}/dev'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
             ),
            self.executed_commands
        )
        self.assertIn(
            'sudo mkdir -p {mounted_root}/sys'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
            ),
            self.executed_commands
        )
        self.assertIn(
            'sudo mkdir -p {mounted_root}/proc'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
             ),
            self.executed_commands
        )
        for subdir_to_check in ('/proc', '/dev', '/sys', '/mnt/vdc1', '/mnt/vdc2'):
            self.assertIn(
                'sudo mkdir -p {mounted_root}{subdir_to_check}'.format(
                    mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint'],
                    subdir_to_check=subdir_to_check,
                ),
                self.executed_commands
            )

    def test_execute__env_mounted(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallationCommand(self.source).execute()

        self.assertIn(
            'sudo mount -o bind {directory} {mounted_root}/mnt/vdc1'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint'],
                directory=self.source.target.device_mapping['vdc']['children']['vdc1']['mountpoint'],
            ),
            self.executed_commands
        )
        self.assertIn(
            'sudo mount -o bind {directory} {mounted_root}/mnt/vdc2'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint'],
                directory=self.source.target.device_mapping['vdc']['children']['vdc2']['mountpoint'],
            ),
            self.executed_commands
        )
        self.assertNotIn(
            'sudo mount -o bind {directory} {mounted_root}/'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint'],
                directory=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint'],
            ),
            self.executed_commands
        )

    def test_execute__dev_mounted(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallationCommand(self.source).execute()

        self.assertIn(
            'sudo mount -o bind /dev {mounted_root}/dev/'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
            ),
            self.executed_commands
        )

    def test_execute__custom_type_env_mounted(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallationCommand(self.source).execute()

        self.assertIn(
            'sudo mount -t proc proc {mounted_root}/proc/'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
             ),
            self.executed_commands
        )
        self.assertIn(
            'sudo mount -t sysfs sys {mounted_root}/sys/'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
            ),
            self.executed_commands
        )

    def test_execute__chrooted_into_mounted_root_and_install_bootloader(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        BootloaderReinstallationCommand(self.source).execute()

        self.assertIn(
            'sudo chroot {mounted_root} sudo grub-install --boot-directory=/boot /dev/{mounted_root_device_id}'.format(
                mounted_root=self.source.target.device_mapping['vda']['children']['vda1']['mountpoint'],
                mounted_root_device_id=self.source.target.device_mapping['vda']['id'],
            ),
            self.executed_commands
        )

    def test_execute__chrooted_into_mounted_root_and_install_bootloader_with_root_mountpoint_on_disk(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.source.remote_host.system_info['block_devices']['vda']['mountpoint'] = \
            self.source.remote_host.system_info['block_devices']['vda']['children']['vda1']['mountpoint']
        self.source.target.device_mapping['vda']['mountpoint'] = \
            self.source.target.device_mapping['vda']['children']['vda1']['mountpoint']
        self.source.target.save()

        BootloaderReinstallationCommand(self.source).execute()

        self.assertIn(
            'sudo chroot {mounted_root} sudo grub-install --boot-directory=/boot /dev/{mounted_root_device_id}'.format(
                mounted_root=self.source.target.device_mapping['vda']['mountpoint'],
                mounted_root_device_id=self.source.target.device_mapping['vda']['id'],
            ),
            self.executed_commands
        )
