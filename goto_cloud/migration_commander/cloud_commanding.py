from cloud_management.public import CloudManager

from command.public import SourceCommand

from remote_execution.public import RemoteHostExecutor

from remote_host.public import RemoteHost

from .source_file_location_resolving import SourceFileLocationResolver


class CloudCommand(SourceCommand):
    """
    base class for SourceCommands which need to use a CloudManager
    """
    def __init__(self, source):
        super().__init__(source)
        self._cloud_manager = CloudManager(self._source.migration_run.plan.plan.get('target_cloud', {}))


class CreateTargetCommand(CloudCommand):
    """
    takes care of creating the the target machine in the cloud
    """
    def _execute(self):
        self._create_target_remote_host(self._create_target_in_cloud())

    def _create_target_in_cloud(self):
        """
        actually creates the target in the cloud

        :return: the cloud metadata returned by the used CloudManager
        :rtype: dict
        """
        return self._cloud_manager.create_target(
            self._source.remote_host.system_info['network']['hostname'],
            self._target.blueprint['bootstrapping_network_interface'],
            self._target.blueprint['network_interfaces'],
            [
                round(disk['size'] / 1024 ** 3)
                for disk in self._source.remote_host.system_info['block_devices'].values()
                if disk['type'] == 'disk'
            ],
            round(self._source.remote_host.system_info['hardware']['ram']['size'] / 1024 ** 2 / 256) * 256,
            len(self._source.remote_host.system_info['hardware']['cpus'])
        )

    def _create_target_remote_host(self, created_target_data):
        """
        creates a remote host for the sources target

        :param created_target_data: the cloud metadata returned while creating the target machine in the cloud
        :type created_target_data: dict
        """
        self._target.remote_host = RemoteHost.objects.create(
            address=next(
                network_interface['ip']
                for network_interface in created_target_data['network_interfaces']
                if network_interface.get('name', '') and '.bootstrap' in network_interface['name']
            ),
            cloud_metadata=created_target_data,
            **self._source.migration_run.plan.plan['target_cloud']['bootstrapping'].get('ssh', {})
        )
        self._target.save()


class StopTargetCommand(CloudCommand):
    def _execute(self):
        RemoteHostExecutor(self._target.remote_host).execute('sudo shutdown -P now &', block_for_response=False)
        self._cloud_manager.stop_target(self._target.remote_host.cloud_metadata['id'])


class DeleteBootstrapVolumeCommand(CloudCommand):
    class NoBootstrapVolumeFoundException(CloudCommand.CommandExecutionException):
        """
        raised if the bootstrap volume could not be deleted, since it wasn't found
        """
        COMMAND_DOES = 'delete the bootstrapping volume'

    ERROR_REPORT_EXCEPTION_CLASS = NoBootstrapVolumeFoundException

    def _execute(self):
        bootstrap_volume = next(
            (
                volume
                for volume in self._target.remote_host.cloud_metadata['volumes']
                if volume.get('name', '') and '.bootstrap' in volume['name']
            ),
            None
        )
        if bootstrap_volume:
            self._cloud_manager.delete_volume(bootstrap_volume['id'])
        else:
            self._add_error('bootstrapping volume could not be found')


class DeleteBootstrapNetworkInterfaceCommand(CloudCommand):
    class NoBootstrapNetworkInterfaceFoundException(CloudCommand.CommandExecutionException):
        """
        raised if the bootstrap network interface could not be deleted, since it wasn't found
        """
        COMMAND_DOES = 'delete the bootstrapping network interface'

    ERROR_REPORT_EXCEPTION_CLASS = NoBootstrapNetworkInterfaceFoundException

    def _execute(self):
        bootstrap_interface = next(
            (
                network_interface
                for network_interface in self._target.remote_host.cloud_metadata['network_interfaces']
                if network_interface.get('name', '') and '.bootstrap' in network_interface['name']
            ),
            None
        )
        if bootstrap_interface:
            self._cloud_manager.delete_nic(self._target.remote_host.cloud_metadata['id'], bootstrap_interface['id'])
            self._update_remote_host()
        else:
            self._add_error('bootstrapping network interface could not be found')

    def _update_remote_host(self):
        source_remote_host = self._source.remote_host
        old_remote_host = self._target.remote_host

        self._target.remote_host = RemoteHost.objects.create(
            address=self._target.blueprint['network_interfaces'][0]['ip'],
            cloud_metadata=old_remote_host.cloud_metadata,
            username=source_remote_host.username,
            os=source_remote_host.os,
            version=source_remote_host.version,
            port=source_remote_host.port,
            password=source_remote_host.password,
            private_key=source_remote_host.private_key,
        )

        self._target.save()
        old_remote_host.delete()


class ConfigureBootDeviceCommand(CloudCommand):
    def _execute(self):
        self._cloud_manager.make_volume_boot(
            self._target.remote_host.cloud_metadata['id'],
            self._get_target_device_to_cloud_volume_id_mapping()[
                SourceFileLocationResolver(self._source).resolve_disk('/boot')
            ],
        )

    def _get_target_device_to_cloud_volume_id_mapping(self):
        mapping = {}

        relevant_cloud_volumes = sorted(
            [
                volume
                for volume in self._target.remote_host.cloud_metadata['volumes']
                if volume.get('name') and '.bootstrap' not in volume['name']
            ],
            key=lambda volume: volume['device_number']
        )
        for index, target_device_id in enumerate(
            sorted(device['id'] for device in self._target.device_mapping.values())
        ):
            mapping[target_device_id] = relevant_cloud_volumes[index]['id']

        return mapping


class StartTargetCommand(CloudCommand):
    def _execute(self):
        self._cloud_manager.start_target(self._target.remote_host.cloud_metadata['id'])
