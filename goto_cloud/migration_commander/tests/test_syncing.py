from unittest.mock import patch

from django.test import TestCase

from commander.public import Commander

from remote_host_command.public import RemoteHostCommand

from ..default_remote_host_commands import DefaultRemoteHostCommand
from ..syncing import SyncCommand, FinalSyncCommand
from ..mountpoint_mapping import MountpointMapper

from .utils import MigrationCommanderTestCase


class TestSyncCommand(MigrationCommanderTestCase):
    def test_execute__sync(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        SyncCommand(self.source).execute()

        self.assertIn(
            'sudo rsync -zaXAPx --delete --numeric-ids -e "ssh -i $HOME/.ssh/id_rsa -o StrictHostKeyChecking=no" '
            '--rsync-path="sudo rsync" {source_dir}/ '
            '{remote_host_address}:{target_dir}'.format(
                source_dir=MountpointMapper.map_mountpoint('/tmp', '/'),
                target_dir=MountpointMapper.map_mountpoint('/mnt', '/'),
                remote_host_address=self.source.target.remote_host.address,
            ),

            self.executed_commands
        )
        self.assertIn(
            'sudo rsync -zaXAPx --delete --numeric-ids -e "ssh -i $HOME/.ssh/id_rsa -o StrictHostKeyChecking=no" '
            '--rsync-path="sudo rsync" {source_dir}/ '
            '{remote_host_address}:{target_dir}'.format(
                source_dir=MountpointMapper.map_mountpoint('/tmp', '/mnt/vdc1'),
                target_dir=MountpointMapper.map_mountpoint('/mnt', '/mnt/vdc1'),
                remote_host_address=self.source.target.remote_host.address,
            ),
            self.executed_commands
        )
        self.assertIn(
            'sudo rsync -zaXAPx --delete --numeric-ids -e "ssh -i $HOME/.ssh/id_rsa -o StrictHostKeyChecking=no" '
            '--rsync-path="sudo rsync" {source_dir}/ '
            '{remote_host_address}:{target_dir}'.format(
                source_dir=MountpointMapper.map_mountpoint('/tmp', '/mnt/vdc2'),
                target_dir=MountpointMapper.map_mountpoint('/mnt', '/mnt/vdc2'),
                remote_host_address=self.source.target.remote_host.address,
            ),
            self.executed_commands
        )

    def test_execute__sync_with_user(self):
        self._init_test_data('ubuntu16', 'target__device_identification')
        self.source.target.remote_host.username = 'testuser'
        self.source.target.remote_host.save()

        SyncCommand(self.source).execute()

        self.assertIn(
            'sudo rsync -zaXAPx --delete --numeric-ids -e "ssh -i $HOME/.ssh/id_rsa -o StrictHostKeyChecking=no" '
            '--rsync-path="sudo rsync" {source_dir}/ '
            'testuser@{remote_host_address}:{target_dir}'
                .format(
                    source_dir=MountpointMapper.map_mountpoint('/tmp', '/'),
                    target_dir=MountpointMapper.map_mountpoint('/mnt', '/'),
                    remote_host_address=self.source.target.remote_host.address,
                ),
            self.executed_commands
        )
        self.assertIn(
            'sudo rsync -zaXAPx --delete --numeric-ids -e "ssh -i $HOME/.ssh/id_rsa -o StrictHostKeyChecking=no" '
            '--rsync-path="sudo rsync" {source_dir}/ '
            'testuser@{remote_host_address}:{target_dir}'
            .format(
                source_dir=MountpointMapper.map_mountpoint('/tmp', '/mnt/vdc1'),
                target_dir=MountpointMapper.map_mountpoint('/mnt', '/mnt/vdc1'),
                remote_host_address=self.source.target.remote_host.address,
            ),
            self.executed_commands
        )
        self.assertIn(
            'sudo rsync -zaXAPx --delete --numeric-ids -e "ssh -i $HOME/.ssh/id_rsa -o StrictHostKeyChecking=no" '
            '--rsync-path="sudo rsync" {source_dir}/ '
            'testuser@{remote_host_address}:{target_dir}'
                .format(
                    source_dir=MountpointMapper.map_mountpoint('/tmp', '/mnt/vdc2'),
                    target_dir=MountpointMapper.map_mountpoint('/mnt', '/mnt/vdc2'),
                    remote_host_address=self.source.target.remote_host.address,
                ),
            self.executed_commands
        )

    def test_execute__temp_mounts_created(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        SyncCommand(self.source).execute()

        self.assertIn(
            'sudo mkdir -p {temp_mountpoint}'.format(
                temp_mountpoint=MountpointMapper.map_mountpoint('/tmp', '/'),
            ),
            self.executed_commands
        )
        self.assertIn(
            'sudo mkdir -p {temp_mountpoint}'.format(
                temp_mountpoint=MountpointMapper.map_mountpoint('/tmp', '/mnt/vdc1'),
            ),
            self.executed_commands
        )
        self.assertIn(
            'sudo mkdir -p {temp_mountpoint}'.format(
                temp_mountpoint=MountpointMapper.map_mountpoint('/tmp', '/mnt/vdc2'),
            ),
            self.executed_commands
        )

    @patch.object(DefaultRemoteHostCommand, 'CHECK_MOUNTPOINT', RemoteHostCommand('I_WILL_FAIL'))
    def test_execute__temp_mounts_mounted(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        SyncCommand(self.source).execute()

        self.assertIn(
            'sudo mount -o bind / {temp_mountpoint}'.format(
                temp_mountpoint=MountpointMapper.map_mountpoint('/tmp', '/'),
            ),
            self.executed_commands
        )
        self.assertIn(
            'sudo mount -o bind /mnt/vdc1 {temp_mountpoint}'.format(
                temp_mountpoint=MountpointMapper.map_mountpoint('/tmp', '/mnt/vdc1'),
            ),
            self.executed_commands
        )
        self.assertIn(
            'sudo mount -o bind /mnt/vdc2 {temp_mountpoint}'.format(
                temp_mountpoint=MountpointMapper.map_mountpoint('/tmp', '/mnt/vdc2'),
            ),
            self.executed_commands
        )

    def test_execute__temp_mounts_not_mounted_twice(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        SyncCommand(self.source).execute()

        self.assertNotIn(
            'sudo mount -o bind / {temp_mountpoint}'.format(
                temp_mountpoint=MountpointMapper.map_mountpoint('/tmp', '/'),
            ),
            self.executed_commands
        )
        self.assertNotIn(
            'sudo mount -o bind /mnt/vdc1 {temp_mountpoint}'.format(
                temp_mountpoint=MountpointMapper.map_mountpoint('/tmp', '/mnt/vdc1'),
            ),
            self.executed_commands
        )
        self.assertNotIn(
            'sudo mount -o bind /mnt/vdc2 {temp_mountpoint}'.format(
                temp_mountpoint=MountpointMapper.map_mountpoint('/tmp', '/mnt/vdc2'),
            ),
            self.executed_commands
        )

    def test_execute__sleep_signal_returned(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.assertEqual(SyncCommand(self.source).execute(), Commander.Signal.SLEEP)

    def test_execute__error_while_syncing(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.source.target.blueprint['commands']['sync'] = 'I_WILL_FAIL'
        self.source.target.save()

        with self.assertRaises(SyncCommand.SyncingException):
            SyncCommand(self.source).execute()


class TestFinalSyncCommand(MigrationCommanderTestCase):
    def test_execute__no_sleep(self):
        self._init_test_data('ubuntu16', 'target__device_identification')

        self.assertIsNone(FinalSyncCommand(self.source).execute())
