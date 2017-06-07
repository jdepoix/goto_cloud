from cloud_management.public import CloudManager

from command.public import SourceCommand

from remote_host.public import RemoteHost


class CreateTargetCommand(SourceCommand):
    """
    takes care of creating the the target machine in the cloud
    """
    def __init__(self, source):
        super().__init__(source)
        self._cloud_manager = CloudManager(self._source.migration_run.plan.plan.get('target_cloud', {}))

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
                if network_interface['name'] and '.bootstrap' in network_interface['name']
            ),
            cloud_metadata=created_target_data,
            **self._source.migration_run.plan.plan['target_cloud']['bootstrapping'].get('ssh', {})
        )
        self._target.save()
