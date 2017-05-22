from unittest import TestCase

import ipaddress

from ..network_mapping import IpDistributor, NetworkMapper, IpValidation


class TestNetworkMapper(TestCase):
    def setUp(self):
        self.network_assigner = NetworkMapper({
            'LAN 1': {
                'net': '0.0.0.0/0',
            },
            'LAN 2': {
                'net': '10.17.32.0/24',
                'gateway': '10.17.32.1',
            },
            'LAN 3': {
                'net': '10.17.33.0/24',
                'gateway': '10.17.33.1',
            },
            'LAN 4': {
                'net': '10.17.34.0/24',
                'gateway': '10.17.34.1',
            }
        })

    def test_init__invalid_gateway(self):
        with self.assertRaises(NetworkMapper.InvalidNetworkSettingsException):
            NetworkMapper({
                'LAN 1': {
                    'net': '10.17.32.0/24',
                    'gateway': '10.17.33.1',
                },
            })

    def test_init__invalid_network_settings(self):
        with self.assertRaises(NetworkMapper.InvalidNetworkSettingsException):
            NetworkMapper({
                'LAN 1': {
                    'gateway': '10.17.33.1',
                },
            })

    def test_map_interface__invalid_static_ip(self):
        with self.assertRaises(NetworkMapper.InvalidNetworkSettingsException):
            self.network_assigner.map_interfaces(
                {
                    'eth0': {
                        'ip': '10.0.2.15',
                        'net_mask': '255.255.255.0',
                        'routes': []
                    },
                },
                {
                    'network_mapping': {
                        '10.0.2.0/24': {
                            'network': 'LAN 2',
                            'static': '10.17.100.100'
                        },
                    },
                }
            )

    def test_map_interface__invalid_blueprint(self):
        with self.assertRaises(NetworkMapper.InvalidNetworkSettingsException):
            self.network_assigner.map_interfaces(
                {
                    'eth0': {
                        'ip': '10.0.2.15',
                        'net_mask': '255.255.255.0',
                        'routes': []
                    },
                },
                {
                    'I': {
                        'am': 'invalid'
                    }
                }
            )

    def test_map_interfaces__no_mapping_found(self):
        with self.assertRaises(NetworkMapper.NoMappingFoundException):
            self.network_assigner.map_interfaces(
                {
                    'eth0': {
                        'ip': '10.0.2.15',
                        'net_mask': '255.255.255.0',
                        'routes': []
                    },
                },
                {
                    'network_mapping': {
                        '192.168.33.0/24': {
                            'network': 'LAN 2',
                            'static': '10.17.32.100'
                        },
                    },
                }
            )

    def test_map_interfaces__public_ip(self):
        self.assertEquals(
            self.network_assigner.map_interfaces(
                {
                    'eth0': {
                        'ip': '8.8.8.8',
                        'net_mask': '0.0.0.0',
                        'routes': []
                    },
                },
                {
                    'network_mapping': {
                        '0.0.0.0/0': {
                            'network': 'LAN 1',
                        },
                    },
                }
            ),
            [
                {
                    'network_id': 'LAN 1',
                    'ip': None,
                    'gateway': None,
                    'net_mask': None,
                    'source_interface': 'eth0'
                },
            ]
        )

    def test_map_interfaces__match_onto_public_ip_if_not_matched(self):
        self.assertEquals(
            self.network_assigner.map_interfaces(
                {
                    'eth0': {
                        'ip': '8.8.8.8',
                        'net_mask': '255.255.0.0',
                        'routes': []
                    },
                },
                {
                    'network_mapping': {
                        '0.0.0.0/0': {
                            'network': 'LAN 1',
                        },
                    },
                }
            ),
            [
                {
                    'network_id': 'LAN 1',
                    'ip': None,
                    'gateway': None,
                    'net_mask': None,
                    'source_interface': 'eth0'
                },
            ]
        )

    def test_map_interfaces(self):
        test_interface_info = {
            'lo': {
                'ip': '127.0.0.1',
                'net_mask': '255.0.0.0',
                'routes': []
            },
            'eth0': {
                'ip': '10.0.2.15',
                'net_mask': '255.255.255.0',
                'routes': [
                    {
                        'net': '0.0.0.0',
                        'gateway': '10.0.2.2',
                        'net_mask': '0.0.0.0'
                    },
                    {
                        'net': '10.0.2.0',
                        'gateway': '0.0.0.0',
                        'net_mask': '255.255.255.0'
                    },
                ]
            },
            'eth1': {
                'ip': '192.168.33.10',
                'net_mask': '255.255.255.0',
                'routes': [
                    {
                        'net': '192.168.33.0',
                        'gateway': '0.0.0.0',
                        'net_mask': '255.255.255.0',
                    },
                ]
            },
        }

        self.assertEqual(
            self.network_assigner.map_interfaces(
                test_interface_info, {
                    'network_mapping': {
                        '192.168.33.0/24': {
                            'network': 'LAN 2',
                            'static': '10.17.32.100'
                        },
                        '10.0.2.0/24': {
                            'network': 'LAN 3',
                            'range': {
                                'from': '10.17.33.10',
                                'to': '10.17.33.30'
                            }
                        }
                    },
                }
            ),
            [
                {
                    'network_id': 'LAN 3',
                    'ip': '10.17.33.10',
                    'gateway': '10.17.33.1',
                    'net_mask': '255.255.255.0',
                    'source_interface': 'eth0'
                },
                {
                    'network_id': 'LAN 2',
                    'ip': '10.17.32.100',
                    'gateway': '10.17.32.1',
                    'net_mask': '255.255.255.0',
                    'source_interface': 'eth1'
                },
            ]
        )

        self.assertEqual(
            self.network_assigner.map_interfaces(
                test_interface_info, {
                    'network_mapping': {
                        '192.168.33.0/24': {
                            'network': 'LAN 2',
                            'range': {
                                'from': '10.17.32.10',
                                'to': '10.17.32.30'
                            }
                        },
                        '10.0.2.0/24': {
                            'network': 'LAN 3',
                            'range': {
                                'from': '10.17.33.10',
                                'to': '10.17.33.30'
                            }
                        }
                    },
                }
            ),
            [
                {
                    'network_id': 'LAN 3',
                    'ip': '10.17.33.11',
                    'gateway': '10.17.33.1',
                    'net_mask': '255.255.255.0',
                    'source_interface': 'eth0'
                },
                {
                    'network_id': 'LAN 2',
                    'ip': '10.17.32.10',
                    'gateway': '10.17.32.1',
                    'net_mask': '255.255.255.0',
                    'source_interface': 'eth1'
                },
            ]
        )


class TestIpDistributor(TestCase):
    def test_get_next_ip(self):
        distributor = IpDistributor(
            ipaddress.ip_address('192.168.0.250'),
            ipaddress.ip_address('192.168.1.105'),
            ipaddress.ip_network('192.168.0.0/16'),
        )

        self.assertEquals(distributor.get_next_ip(), '192.168.0.250')
        self.assertEquals(distributor.get_next_ip(), '192.168.0.251')
        self.assertEquals(distributor.get_next_ip(), '192.168.0.252')
        self.assertEquals(distributor.get_next_ip(), '192.168.0.253')
        self.assertEquals(distributor.get_next_ip(), '192.168.0.254')
        self.assertEquals(distributor.get_next_ip(), '192.168.0.255')
        self.assertEquals(distributor.get_next_ip(), '192.168.1.0')
        self.assertEquals(distributor.get_next_ip(), '192.168.1.1')
        self.assertEquals(distributor.get_next_ip(), '192.168.1.2')

    def test_get_next_ip__skip_net_address(self):
        distributor = IpDistributor(
            ipaddress.ip_address('192.168.0.0'),
            ipaddress.ip_address('192.168.0.105'),
            ipaddress.ip_network('192.168.0.0/24'),
        )

        self.assertEquals(distributor.get_next_ip(), '192.168.0.1')

    def test_get_next_ip__skip_broadcast_address(self):
        distributor = IpDistributor(
            ipaddress.ip_address('192.168.0.254'),
            ipaddress.ip_address('192.168.0.255'),
            ipaddress.ip_network('192.168.0.0/24'),
        )

        self.assertEquals(distributor.get_next_ip(), '192.168.0.254')
        with self.assertRaises(IpDistributor.RangeExhaustedException):
            distributor.get_next_ip()

    def test_get_next_ip__range_exhausted(self):
        distributor = IpDistributor(
            ipaddress.ip_address('192.168.0.100'),
            ipaddress.ip_address('192.168.0.104'),
            ipaddress.ip_network('192.168.0.0/24'),
        )

        distributor.get_next_ip()
        distributor.get_next_ip()
        distributor.get_next_ip()
        distributor.get_next_ip()
        distributor.get_next_ip()

        with self.assertRaises(IpDistributor.RangeExhaustedException):
            distributor.get_next_ip()


class TestIpValidation(TestCase):
    def test_validate_ip_address(self):
        self.assertEquals(
            IpValidation.validate_ip_address('192.168.0.3'),
            ipaddress.ip_address('192.168.0.3')
        )

    def test_validate_ip_address__invalid(self):
        with self.assertRaises(IpValidation.InvalidIpException):
            IpValidation.validate_ip_address('192.168.0.333')

    def test_validate_net_address(self):
        self.assertEquals(
            IpValidation.validate_net_address('192.168.0.0/16'),
            ipaddress.ip_network('192.168.0.0/16')
        )

    def test_validate_net_address__invalid(self):
        with self.assertRaises(IpValidation.InvalidIpException):
            IpValidation.validate_net_address('192.168.0.0/333')

    def test_validate_ip_range__from_not_in_net(self):
        with self.assertRaises(IpValidation.InvalidRangeException):
            IpValidation.validate_ip_range(
                ipaddress.ip_address('192.168.1.10'),
                ipaddress.ip_address('192.168.0.100'),
                ipaddress.ip_network('192.168.0.0/24'),
            )

    def test_validate_ip_range__to_not_in_net(self):
        with self.assertRaises(IpValidation.InvalidRangeException):
            IpValidation.validate_ip_range(
                ipaddress.ip_address('192.168.0.10'),
                ipaddress.ip_address('192.168.1.100'),
                ipaddress.ip_network('192.168.0.0/24'),
            )

    def test_validate_ip_range__to_lt_from(self):
        with self.assertRaises(IpValidation.InvalidRangeException):
            IpValidation.validate_ip_range(
                ipaddress.ip_address('192.168.0.100'),
                ipaddress.ip_address('192.168.0.10'),
                ipaddress.ip_network('192.168.0.0/24'),
            )
