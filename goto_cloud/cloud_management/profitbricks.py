import time

from profitbricks.client import ProfitBricksService, Server, Volume, NIC

from enums.public import StringEnum

from .cloud_adapter import CloudAdapter


class ProfitbricksAdapter(CloudAdapter):
    """
    cloud adapter for the profitbricks cloud provider
    """
    class EntityState(StringEnum):
        """
        represents the state a REST entity can have
        """
        AVAILABLE = 'AVAILABLE'
        INACTIVE = 'INACTIVE'
        BUSY = 'BUSY'

    class RequestState(StringEnum):
        """
        represents the state a request can have
        """
        DONE = 'DONE'

    def __init__(self, settings):
        super().__init__(settings)
        self._client = ProfitBricksService(
            username=settings['login']['username'],
            password=settings['login']['password'],
        )

    @property
    def _datacenter(self):
        """
        shortcut to the datacenter id
        
        :return: datacenter id
        :rtype: str
        """
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

    def create_target(self, name, bootstrapping_network_interface, network_interfaces, volumes, ram, cores):
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
                            lan=self._settings['networks'][bootstrapping_network_interface['network_id']]['cloud_id'],
                            name='{hostname}.bootstrap'.format(
                                hostname=name,
                            ),
                            **{'ips': [bootstrapping_network_interface['ip']]}
                            if bootstrapping_network_interface['ip'] else {},
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

        return {
            'id': response['id'],
            'volumes': [
                {
                    'id': volume['id'],
                    'device_number': volume['properties']['deviceNumber'],
                    'size': volume['properties']['size'],
                    'name': volume['properties']['name'],
                }
                for volume in self._client.get_attached_volumes(
                    datacenter_id=self._datacenter, server_id=response['id']
                )['items']
            ],
            'network_interfaces': [
                {
                    'id': network_interface['id'],
                    'name': network_interface['properties']['name'],
                    'lan': network_interface['properties']['lan'],
                    'ip': network_interface['properties']['ips'][0],
                }
                for network_interface in self._client.list_nics(
                    datacenter_id=self._datacenter, server_id=response['id']
                )['items']
            ],
        }

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
        """
        waits for a REST entity to reach a certain state
        
        :param retrieve_entity_function: the function to retrieve the state
        :type retrieve_entity_function: (**kwargs) -> Any
        :param retrieve_entity_function_kwargs: the kwargs used for calling the function
        :type retrieve_entity_function_kwargs: dict
        :param expected_entity_state: the expected state
        :type expected_entity_state: str | (str) -> bool
        :param timeout: the number of seconds to wait in between tries
        :type timeout: int | float
        :param try_for_mins: the number of minutes to try overall
        :type try_for_mins: int | float
        """
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
        """
        waits until a request of the given id is done
        
        :param request_id: the request to wait for
        :type request_id: str
        """
        self._wait_for(
            lambda: self._client.get_request(
                request_id=request_id,
                status=True,
            ).get('metadata', {}).get('status', ''),
            {},
            ProfitbricksAdapter.RequestState.DONE,
        )

    def _wait_for(self, retrieve_function, retrieve_function_kwargs, expected_state, timeout=10, try_for_mins=60):
        """
        waits for a given function to retrieve a given state
        
        :param retrieve_function: the function to retrieve the state
        :type retrieve_function: (**kwargs) -> Any
        :param retrieve_function_kwargs: the kwargs used for calling the function
        :type retrieve_function_kwargs: dict
        :param expected_state: the expected state
        :type expected_state: str | (str) -> bool
        :param timeout: the number of seconds to wait in between tries
        :type timeout: int | float
        :param try_for_mins: the number of minutes to try overall
        :type try_for_mins: int | float
        """
        tries = 0
        current_state = retrieve_function(**retrieve_function_kwargs)

        while (
                not expected_state(current_state)
                if callable(expected_state)
                else current_state != expected_state
        ):
            if float(tries) >= try_for_mins / timeout * 60:
                raise self.CloudConnectionException(
                    'Could not retrieve the expected state from profitbricks!'
                )
            tries += 1
            time.sleep(timeout)
            current_state = retrieve_function(**retrieve_function_kwargs)
