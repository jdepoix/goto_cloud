from command.public import SourceCommand

from remote_execution.public import RemoteHostExecutor

from remote_host_command.public import RemoteHostCommand

from .default_remote_host_commands import DefaultRemoteHostCommand
from .source_file_location_resolving import SourceFileLocationResolver


class BootloaderReinstallationCommand(SourceCommand):
    """
    Takes care of reinstalling in the target environment before go live. To do this, the copied source root directory
    will be chrooted and then the bootloader reinstall command from the migration plan will be executed. To avoid errors
    in the chrooted environment, important temp filesystems like proc, sys and dev will be mounted into the directory,
    which will be chrooted, before the chroot actually happens.
    """
    class InstallationException(SourceCommand.CommandExecutionException):
        """
        raised if something goes wrong, while trying to reinstall the bootloader
        """
        COMMAND_DOES = 'reinstall the bootloader'

    ERROR_REPORT_EXCEPTION_CLASS = InstallationException
    MOUNT_CUSTOM_TYPE_COMMAND = RemoteHostCommand('sudo mount -t {TYPE} {NAME} {MOUNTPOINT}')
    CHROOT_COMMAND = RemoteHostCommand('sudo chroot {DIRECTORY} {COMMAND}')

    def __init__(self, source):
        super().__init__(source)
        self.source_file_location_resolver = SourceFileLocationResolver(self._source)

    @SourceCommand._collect_errors
    def _execute(self):
        root_source_mountpoint = self._find_root_source_mountpoint()
        remote_executor = RemoteHostExecutor(self._target.remote_host)
        self._create_source_environment_mountpoints(remote_executor, root_source_mountpoint)
        self._mount_source_environment(remote_executor, root_source_mountpoint)
        self._mount_source_mountpoints(remote_executor, root_source_mountpoint)
        self._reinstall_bootloader(remote_executor, root_source_mountpoint)

    def _mount_source_environment(self, remote_executor, root_source_mountpoint):
        """
        mounts temp filesystems in the chroot environment 
        
        :param remote_executor: the remote executor to execute the create commands with
        :type remote_executor: RemoteHostExecutor
        :param root_source_mountpoint: the directory which maps the sources root directory
        :type root_source_mountpoint: str
        """
        remote_executor.execute(
            self.MOUNT_CUSTOM_TYPE_COMMAND.render(
                type='proc',
                name='proc',
                mountpoint=root_source_mountpoint + '/proc/'
            )
        )
        remote_executor.execute(
            self.MOUNT_CUSTOM_TYPE_COMMAND.render(
                type='sysfs',
                name='sys',
                mountpoint=root_source_mountpoint + '/sys/'
            )
        )
        remote_executor.execute(
            DefaultRemoteHostCommand.BIND_MOUNT.render(
                directory='/dev',
                mountpoint=root_source_mountpoint + '/dev/'
            )
        )

    def _reinstall_bootloader(self, remote_executor, root_source_mountpoint):
        """
        executes the reinstall bootloader command in the chrooted environment
        
        :param remote_executor: 
        :param root_source_mountpoint: 
        :return: 
        """
        remote_executor.execute(
            self.CHROOT_COMMAND.render(
                directory=root_source_mountpoint,
                command=RemoteHostCommand(self._target.blueprint['commands']['reinstall_bootloader']).render(
                    device='/dev/{device_id}'.format(
                        device_id=self._find_target_device_id_by_mountpoint(root_source_mountpoint)
                    )
                )
            )
        )

    def _find_root_source_mountpoint(self):
        """
        finds the mountpoint which the sources root data is copied in
        
        :return: mountpoint for sources root data
        :rtype: str
        """
        return self.source_file_location_resolver.resolve('/')

    def _create_source_environment_mountpoints(self, remote_executor, root_source_mountpoint):
        """
        creates the directory where the temp filesystems will be mounted
        
        :param remote_executor: the remote executor to execute the commands with
        :type remote_executor: RemoteHostExecutor
        :param root_source_mountpoint: the directory which maps the sources root directory
        :type root_source_mountpoint: str 
        """
        for source_environment_dir in ('/sys', '/proc', '/dev',):
            remote_executor.execute(
                DefaultRemoteHostCommand.MAKE_DIRECTORY.render(
                    directory=root_source_mountpoint + source_environment_dir
                )
            )

    def _find_target_device_id_by_mountpoint(self, mountpoint):
        """
        finds a targets disk device id, on which a given mountpoint is mounted
        
        :param mountpoint: the mountpoint you are looking for
        :type mountpoint: str
        :return: device id
        :rtype: str
        """
        for device in self._target.device_mapping.values():
            if device['mountpoint'] == mountpoint:
                return device['id']

            for partition in device['children'].values():
                if partition['mountpoint'] == mountpoint:
                    return device['id']

    def _mount_source_mountpoints(self, remote_executor, root_source_mountpoint):
        for device in self._source.remote_host.system_info['block_devices'].values():
            if device['mountpoint'] and device['mountpoint'] != '/':
                self._mount_source_mountpoint(remote_executor, root_source_mountpoint, device['mountpoint'])

            for partition in device['children'].values():
                if partition['mountpoint'] and partition['mountpoint'] != '/':
                    self._mount_source_mountpoint(remote_executor, root_source_mountpoint, partition['mountpoint'])

    def _mount_source_mountpoint(self, remote_executor, root_source_mountpoint, mountpoint):
        chrooted_env_location = root_source_mountpoint + mountpoint

        try:
            resolved_base_path = self.source_file_location_resolver.resolve(mountpoint)
            remote_executor.execute(
                DefaultRemoteHostCommand.MAKE_DIRECTORY.render(
                    directory=chrooted_env_location
                )
            )
            remote_executor.execute(
                DefaultRemoteHostCommand.BIND_MOUNT.render(
                    directory=resolved_base_path,
                    mountpoint=chrooted_env_location
                )
            )
        except SourceFileLocationResolver.InvalidPathException:
            pass
