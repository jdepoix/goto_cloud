from enums.public import StringEnum

from .cloud_adapter import CloudAdapter
from .profitbricks import ProfitbricksAdapter


class CloudProvider(StringEnum):
    """
    enum of cloud providers
    """
    class UnsupportedProviderException(Exception):
        """
        raised if a cloud provider is not supported
        """
        def __init__(self, provider_name):
            super().__init__('The cloud provider {provider_name} is currently not supported!'.format(
                provider_name=provider_name
            ))

    PROFITBRICKS = 'PB'


class CloudManager(CloudAdapter):
    """
    provides an API to the operations executed in a cloud, but abstracts the actually used provider away
    """
    _PROVIDER_TO_ADAPTER_MAPPING = {
        CloudProvider.PROFITBRICKS: ProfitbricksAdapter
    }
    """
    maps a cloud provider onto the CloudAdapter which supports it
    """

    def __init__(self, settings):
        super().__init__(settings)
        self._adapter = self._get_supported_cloud_adapter(settings)

    def _get_supported_cloud_adapter(self, settings):
        """
        returns a instance of a supported cloud adapter
        
        :param settings: the cloud settings from the migration plan
        :type settings: dict
        :return: an instance of a supported cloud adapter
        :rtype: CloudAdapter
        :raises CloudProvider.UnsupportedProviderException: if the provider in the settings is not supported
        """
        if 'provider' not in settings:
            raise CloudAdapter.InvalidCloudSettingsException(
                'The cloud settings are not specifying which cloud provider should be used'
            )
        if settings['provider'] not in self._PROVIDER_TO_ADAPTER_MAPPING:
            raise CloudProvider.UnsupportedProviderException(settings['provider'])

        return self._PROVIDER_TO_ADAPTER_MAPPING[settings['provider']](settings)

    def start_target(self, server_id):
        return self._adapter.start_target(server_id)

    def stop_target(self, server_id):
        return self._adapter.stop_target(server_id)

    def delete_target(self, server_id):
        return self._adapter.delete_target(server_id)

    def create_target(self, name, network_interfaces, volumes, ram, cores):
        return self._adapter.create_target(name, network_interfaces, volumes, ram, cores)

    def delete_volume(self, volume_id):
        return self._adapter.delete_volume(volume_id)

    def make_volume_boot(self, server_id, volume_id):
        return self._adapter.make_volume_boot(server_id, volume_id)

    def delete_nic(self, server_id, nic_id):
        return self._adapter.delete_nic(server_id, nic_id)
