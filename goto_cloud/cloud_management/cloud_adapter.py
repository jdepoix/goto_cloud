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
    def create_target(self, name, bootstrapping_network_interface, network_interfaces, volumes, ram, cores):
        """
        creates a target machine in the cloud
        
        :param bootstrapping_network_interface:
        :param name: the name of the target machine
        :type name: str
        :param bootstrapping_network_interface: the network interface which is used during the migration
        :type bootstrapping_network_interface: {'ip: str, 'network_id': str}
        :param network_interfaces: the network interfaces which should be created
        :type network_interfaces: [{'ip: str, 'network_id': str}]
        :param volumes: a list of volume sizes in gb, which should be created
        :type volumes: list[int]
        :param ram: the ram size in mb as a multiple of 256
        :type ram: int
        :param cores: the number of cores the target machine should get
        :type cores: int
        :return: the created target
        :rtype: dict
        """
        pass

    @abstractmethod
    def delete_target(self, server_id):
        """
        deletes the target with the given id
        
        :param server_id: the cloud id of the target machine
        :type server_id: str
        """
        pass

    @abstractmethod
    def start_target(self, server_id):
        """
        starts the target with the given id and waits for it to be started

        :param server_id: the cloud id of the target machine
        :type server_id: str
        """
        pass

    @abstractmethod
    def stop_target(self, server_id):
        """
        stops the target with the given id and waits for it to be stopped

        :param server_id: the cloud id of the target machine
        :type server_id: str
        """
        pass

    @abstractmethod
    def delete_volume(self, volume_id):
        """
        deletes the volume with the given id

        :param volume_id: the volume id of the volume which should be deleted
        :type volume_id: str
        """
        pass

    @abstractmethod
    def make_volume_boot(self, server_id, volume_id):
        """
        changes which device a target machine should boot from and waits for the change to be finished
        
        :param server_id: the cloud id of the target machine
        :type server_id: str 
        :param volume_id: the volume id of the volume which should become the new boot device
        :type volume_id: str 
        :return: 
        """
        pass

    @abstractmethod
    def delete_nic(self, server_id, nic_id):
        """
        deletes the network interface with the given id
        
        :param server_id: the cloud id of the target machine
        :type server_id: str 
        :param nic_id: the volume id of the volume which should be deleted
        :type nic_id: str
        """
        pass
