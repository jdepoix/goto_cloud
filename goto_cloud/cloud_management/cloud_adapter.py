from abc import ABCMeta, abstractmethod


class CloudAdapter(metaclass=ABCMeta):
    """
    defines an interface which should be used to implement functionality for a cloud provider
    """
    class CloudConnectionException(Exception):
        """
        raised if something goes wrong, while communicating with the cloud
        """

    class InvalidCloudSettingsException(Exception):
        """
        raised if the given cloud settings are not valid
        """
        pass

    def __init__(self, settings):
        self._settings = settings

    @abstractmethod
    def create_target(self, name, network_interfaces, volumes, ram, cores):
        pass

    @abstractmethod
    def delete_target(self, server_id):
        pass

    @abstractmethod
    def start_target(self, server_id):
        pass

    @abstractmethod
    def stop_target(self, server_id):
        pass

    @abstractmethod
    def delete_volume(self, volume_id):
        pass

    @abstractmethod
    def make_volume_boot(self, server_id, volume_id):
        pass

    @abstractmethod
    def delete_nic(self, server_id, nic_id):
        pass
