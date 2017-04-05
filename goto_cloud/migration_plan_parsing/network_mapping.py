import ipaddress


class IpValidation():
    """
    set of static functions, used to validate ips
    """
    class InvalidIpException(Exception):
        """
        is raise if a ip is not valid
        """
        def __init__(self, ip_string):
            """
            :param ip_string: the ip which caused this exception
            :type ip_string: str
            """
            super().__init__('the ip: "{ip_string}" is not valid'.format(ip_string=ip_string))

    class InvalidRangeException(Exception):
        """
        is raised if a range is not valid
        """
        def __init__(self, from_ip, to_ip, net_address, gateway_ip=None):
            """
            :param from_ip: the ranges from address
            :type from_ip: ipaddress.IPv4Address or ipaddress.IPv6Address  
            :param to_ip: the ranges to address
            :type to_ip: ipaddress.IPv4Address or ipaddress.IPv6Address 
            :param net_address: the ranges net adress
            :type net_address: ipaddress.IPv4Network or ipaddress.IPv6Network
            :param gateway_ip: optional gateway address
            :type gateway_ip: ipaddress.IPv4Address or ipaddress.IPv6Address
            """
            super().__init__(
                (
                    'invalid range! '
                    'the net address ({net_address}), {gateway_info}the from ip ({from_ip}) '
                    'and to ip ({to_ip}) do not match'
                ).format(
                    net_address=str(net_address),
                    from_ip=str(from_ip),
                    to_ip=str(to_ip),
                    gateway_info='the gateway ({gateway_ip}), '.format(gateway_ip=str(gateway_ip)) if gateway_ip else ''
                )
            )

    @staticmethod
    def validate_ip_address(ip_string):
        """
        validates an ip given as a string
        
        :param ip_string: the ip to validate
        :type ip_string: str
        :return: the validated ip
        :rtype: ipaddress.IPv4Address or ipaddress.IPv6Address
        :raises IpValidation.InvalidIpException: if ip is not valid
        """
        return IpValidation._validate_ip_cast(ip_string, ipaddress.ip_address)

    @staticmethod
    def validate_net_address(ip_string):
        """
        validates an net address ip given as a string

        :param ip_string: the ip to validate
        :type ip_string: str
        :return: the validated ip
        :rtype: ipaddress.IPv4Network or ipaddress.IPv6Network
        :raises IpValidation.InvalidIpException: if ip is not valid
        """
        return IpValidation._validate_ip_cast(ip_string, ipaddress.ip_network)

    @staticmethod
    def validate_ip_range(from_ip, to_ip, net_address, gateway_ip=None):
        """
        validate a ip range
        
        :param from_ip: the ranges from address
        :type from_ip: ipaddress.IPv4Address or ipaddress.IPv6Address  
        :param to_ip: the ranges to address
        :type to_ip: ipaddress.IPv4Address or ipaddress.IPv6Address 
        :param net_address: the ranges net adress
        :type net_address: ipaddress.IPv4Network or ipaddress.IPv6Network
        :param gateway_ip: optional gateway address
        :type gateway_ip: ipaddress.IPv4Address or ipaddress.IPv6Address
        :raises IpValidation.InvalidRangeException: if range is not valid
        """
        if (
            from_ip not in net_address
            or to_ip not in net_address
            or from_ip > to_ip
            or gateway_ip and gateway_ip not in net_address
        ):
            raise IpValidation.InvalidRangeException(from_ip, to_ip, net_address, gateway_ip)

    @staticmethod
    def _validate_ip_cast(ip_string, cast_function):
        try:
            return cast_function(ip_string)
        except ValueError:
            raise IpValidation.InvalidIpException(ip_string)


class NetworkMapper():
    """
    takes care of assigning network settings for a given blueprint, to given interfaces
    """
    class InvalidNetworkSettingsException(Exception):
        """
        is raised if network settings are not valid
        """
        pass

    class NoMappingFoundException(Exception):
        """
        is raised if there is a ip which no mapping was found for
        """
        pass

    def __init__(self, network_settings):
        """
        is initialized with the network settings it should use
        
        :param network_settings: the network settings to use
        :type network_settings: dict
        """
        self.networks = self._create_network_structure(network_settings)

    def map_interfaces(self, interfaces, blueprint):
        """
        maps a set of interfaces onto their new interfaces, considering the network settings and the given blueprint
        
        :param interfaces: dict of interfaces
        :type interfaces: dict
        :param blueprint: blueprint which is used to map the interfaces
        :type blueprint: dict
        :return: a list of dicts representing the new interfaces
        :rtype: list[dict]
        """
        try:
            mapped_interfaces = []
            network_mapping = self._create_network_mapping(blueprint)

            for interface_id, interface in interfaces.items():
                if not IpValidation.validate_ip_address(interface['ip']).is_loopback:
                    network = self._map_network(interface['ip'], interface['net_mask'], network_mapping)
                    ip = self._get_ip(network)
                    mapped_interfaces.append({
                        'network_id': network['network_id'],
                        'ip': str(ip) if ip else None,
                        'gateway': str(self.networks[network['network_id']]['gateway'])
                                    if self.networks[network['network_id']]['gateway'] else None,
                        'net_mask': str(self.networks[network['network_id']]['net_address'].netmask) if ip else None,
                        'source_interface': interface_id,
                    })

            return mapped_interfaces
        except KeyError:
            raise NetworkMapper.InvalidNetworkSettingsException(
                'following blueprint network mapping is not valid:\n{blueprint}'.format(
                    blueprint=str(blueprint)
                )
            )

    def _map_network(self, ip_string, net_mask_string, network_mapping):
        ip = IpValidation.validate_ip_address(ip_string)
        net_mask = IpValidation.validate_ip_address(net_mask_string)

        net_address = next(
            (net_address for net_address in network_mapping if ip in net_address and net_address.netmask == net_mask),
            None
        )

        if net_address is None:
            raise NetworkMapper.NoMappingFoundException(
                'no matching network mapping was found, for the following ip: {ip}'.format(ip=str(ip))
            )

        return network_mapping[net_address]

    def _get_ip(self, network):
        if 'static' in network:
            static_ip = IpValidation.validate_ip_address(network['static'])

            if static_ip not in self.networks[network['network_id']]['net_address']:
                raise NetworkMapper.InvalidNetworkSettingsException(
                    'static ip "{static_ip}" does not fit into the network "{net_address}"'.format(
                        static_ip=str(static_ip),
                        net_address=str(self.networks[network['network_id']]['net_address']),
                    )
                )

            return static_ip
        if 'range' in network:
            return self._get_ip_distributor(
                network['network_id'],
                IpValidation.validate_ip_address(network['range']['from']),
                IpValidation.validate_ip_address(network['range']['to']),
            ).get_next_ip()

        return None

    def _get_ip_distributor(self, network_id, from_ip, to_ip):
        if (from_ip, to_ip,) not in self.networks[network_id]['distributors']:
            self.networks[network_id]['distributors'][(from_ip, to_ip,)] = IpDistributor(
                from_ip, to_ip, self.networks[network_id]['net_address']
            )

        return self.networks[network_id]['distributors'][(from_ip, to_ip,)]

    def _create_network_mapping(self, blueprint):
        network_mapping = {}

        for net_address_string, mapping_config in blueprint['network_mapping'].items():
            net_address = IpValidation.validate_net_address(net_address_string)
            network_mapping[net_address] = {
                'network_id': mapping_config['network']
            }

            if 'static' in mapping_config:
                network_mapping[net_address]['static'] = mapping_config['static']
            elif 'range' in mapping_config:
                network_mapping[net_address]['range'] = mapping_config['range']

        return network_mapping

    def _create_network_structure(self, network_settings):
        try:
            networks = {}

            for network_id in network_settings:
                net_address = IpValidation.validate_net_address(network_settings[network_id]['net'])
                gateway_address = None
                if 'gateway' in network_settings[network_id]:
                    gateway_address = IpValidation.validate_ip_address(network_settings[network_id]['gateway'])
                    if gateway_address not in net_address:
                        raise NetworkMapper.InvalidNetworkSettingsException(
                            (
                                'network {network_id} is not valid! '
                                'gateway ip ({gateway_ip}) does not match the net address ({net_address})'
                            ).format(network_id=network_id, gateway_address=gateway_address, net_address=net_address)
                        )

                networks[network_id] = {
                    'net_address': net_address,
                    'gateway': gateway_address,
                    'distributors': {},
                }

            return networks
        except KeyError:
            raise NetworkMapper.InvalidNetworkSettingsException(
                'the following network settings are not valid:\n{network_settings}'.format(
                    network_settings=str(network_settings)
                )
            )


class IpDistributor():
    """
    takes care of distributing ips of a given net in a given range
    """
    class RangeExhaustedException(Exception):
        """
        is raised when the range is exhausted
        """
        def __init__(self, from_ip, to_ip):
            """
            :param from_ip: the ranges from address
            :type from_ip: ipaddress.IPv4Address or ipaddress.IPv6Address  
            :param to_ip: the ranges to address
            :type to_ip: ipaddress.IPv4Address or ipaddress.IPv6Address 
            """
            super().__init__('the ip range ({from_ip} - {to_ip}) is exhausted!'.format(
                from_ip=from_ip,
                to_ip=to_ip,
            ))

    def __init__(self, from_ip, to_ip, net_address):
        """
        initialized with a given range, in a given network
        
        :param from_ip: the ip the ranges starts at
        :type from_ip: str
        :param to_ip: the ip the range stops it (included)
        :type to_ip: str
        :param net_address: the network address, in which the ips are distributed
        :type net_address: str
        :raises IpValidation.InvalidIpException: if a ip is not valid
        :raises IpValidation.InvalidRangeException: if range is not valid
        """
        self.last_distributed_ip = None
        self.from_ip = IpValidation.validate_ip_address(from_ip)
        self.to_ip = IpValidation.validate_ip_address(to_ip)
        self.net_address = IpValidation.validate_net_address(net_address)

        IpValidation.validate_ip_range(self.from_ip, self.to_ip, self.net_address)

    def get_next_ip(self):
        """
        gets the next available ip address
        
        :return: ip address
        :rtype: str
        :raises IpValidation.RangeExhaustedException: raised if range is exhausted
        """
        if self.last_distributed_ip:
            self.last_distributed_ip = self.last_distributed_ip + 1
        else:
            self.last_distributed_ip = self.from_ip

        if self.last_distributed_ip > self.to_ip:
            raise IpDistributor.RangeExhaustedException(self.from_ip, self.to_ip)

        if (
            self.last_distributed_ip == self.net_address.network_address
            or self.last_distributed_ip == self.net_address.broadcast_address
        ):
            return self.get_next_ip()

        return str(self.last_distributed_ip)
