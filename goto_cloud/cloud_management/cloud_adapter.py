import time

from abc import ABCMeta, abstractmethod

from profitbricks.client import ProfitBricksService, Server, NIC, Volume

from enums.public import StringEnum


class CloudAdapter(metaclass=ABCMeta):
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


class ProfitbricksAdapter(CloudAdapter):
    class EntityState(StringEnum):
        AVAILABLE = 'AVAILABLE'
        INACTIVE = 'INACTIVE'
        BUSY = 'BUSY'

    class RequestState(StringEnum):
        DONE = 'DONE'

    def __init__(self, settings):
        super().__init__(settings)
        self._client = ProfitBricksService(
            username=settings['login']['username'],
            password=settings['login']['password'],
        )

    @property
    def _datacenter(self):
        return self._settings['datacenter']

    def start_target(self, server_id):
        response = self._client.start_server(datacenter_id=self._datacenter, server_id=server_id)
        self._wait_for_entity_state(
            self._client.get_server, {'server_id': server_id}, ProfitbricksAdapter.EntityState.AVAILABLE
        )
        return response

    def stop_target(self, server_id):
        response = self._client.stop_server(datacenter_id=self._datacenter, server_id=server_id)
        self._wait_for_entity_state(
            self._client.get_server, {'server_id': server_id}, ProfitbricksAdapter.EntityState.INACTIVE
        )
        return response

    def delete_target(self, server_id):
        return self._client.delete_server(datacenter_id=self._datacenter, server_id=server_id)

    def create_target(self, name, network_interfaces, volumes, ram, cores):
        try:
            # noinspection PyTypeChecker
            response = self._client.create_server(
                datacenter_id = self._datacenter,
                server = Server(
                    name=name,
                    cores=cores,
                    ram=ram,
                    create_volumes=[
                        Volume(
                            name='{hostname}.bootstrap'.format(
                                hostname=name,
                            ),
                            image=self._settings['bootstrapping']['template_id'],
                            size=self._settings['bootstrapping']['size'],
                        ),
                        *[
                            Volume(
                                name='{hostname}.clone-{volume_index}'.format(
                                    hostname=name,
                                    volume_index=volume_index,
                                ),
                                size=str(volume_size)
                            )
                            for volume_index, volume_size in enumerate(volumes)
                        ]
                    ],
                    nics=[
                        NIC(
                            lan=self._settings['networks'][self._settings['bootstrapping']['network']]['cloud_id'],
                            name='{hostname}.bootstrap'.format(
                                hostname=name,
                            ),
                        ),
                        *[
                            NIC(
                                lan=self._settings['networks'][network_interface['network_id']]['cloud_id'],
                                **{'ips': [network_interface['ip']]} if network_interface['ip'] else {},
                            )
                            for network_interface in network_interfaces
                        ]
                    ],
                )
            )
        except KeyError:
            raise self.InvalidCloudSettingsException(
                'The target_cloud settings in the migration plan are invalid!'
            )
        self._wait_for_request(response['requestId'])

        return response

    def delete_volume(self, volume_id):
        return self._client.delete_volume(datacenter_id=self._datacenter, volume_id=volume_id)

    def make_volume_boot(self, server_id, volume_id):
        response = self._client.update_server(
            datacenter_id=self._datacenter, server_id=server_id, boot_volume_id=volume_id
        )
        self._wait_for_entity_state(
            self._client.get_server,
            {'server_id': server_id},
            lambda state: state != ProfitbricksAdapter.EntityState.BUSY
        )
        return response

    def delete_nic(self, server_id, nic_id):
        return self._client.delete_nic(datacenter_id=self._datacenter, server_id=server_id, nic_id=nic_id)

    def _wait_for_entity_state(
        self,
        retrieve_entity_function,
        retrieve_entity_function_kwargs,
        expected_entity_state,
        timeout=10,
        try_for_mins=60,
    ):
        self._wait_for(
            lambda: retrieve_entity_function(
                datacenter_id=self._datacenter, **retrieve_entity_function_kwargs
            ).get('metadata', {}).get('state', ''),
            {},
            expected_entity_state,
            timeout,
            try_for_mins,
        )

    def _wait_for_request(self, request_id):
        self._wait_for(
            lambda: self._client.get_request(
                request_id=request_id,
                status=True,
            ).get('metadata', {}).get('status', ''),
            {},
            ProfitbricksAdapter.RequestState.DONE,
        )

    def _wait_for(self, retrieve_function, retrieve_function_kwargs, expected_state, timeout=10, try_for_mins=60):
        tries = 0
        current_state = retrieve_function(**retrieve_function_kwargs)

        while (
                not expected_state(current_state)
                if callable(expected_state)
                else current_state != expected_state
        ):
            if float(tries) >= try_for_mins / timeout * 60:
                raise ProfitbricksAdapter.CloudConnectionException(
                    'Could not retrieve the expected state from profitbricks!'
                )
            tries += 1
            time.sleep(timeout)
            current_state = retrieve_function(**retrieve_function_kwargs)
