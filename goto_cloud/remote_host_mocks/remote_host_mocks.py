import os
from io import BytesIO

from settings.base import BASE_DIR


class RemoteHostMock(object):
    def __init__(self, commands, expected_config):
        self.commands = commands
        self.expected_config = expected_config

    def execute(self, command):
        actual_command = next((known_command for known_command in self.commands if known_command in command), None)

        return (
            (BytesIO(), BytesIO(self.commands[actual_command].encode()), BytesIO())
            if actual_command
            else (BytesIO(), BytesIO(), BytesIO(b'Command does not exist!'))
        )

    def get_config(self):
        return self.expected_config

    @staticmethod
    def create_from_file(
        commands_root_directory_path,
        filename,
        command_directory_map,
        expected_config,
    ):
        commands_root_directory = os.path.realpath(commands_root_directory_path)
        commands = {}

        for command in command_directory_map:
            with open(
                os.path.join(os.path.join(commands_root_directory, command_directory_map[command]), filename)
            ) as command_output:
                commands[command] = command_output.read()
        return RemoteHostMock(commands, expected_config)


COMMANDS_OUTPUT_ROOT_DIRECTORY_PATH = BASE_DIR + '/remote_host_mocks/assets/test_vms_command_output'
COMMAND_DIRECTORY_MAP = {
    'cat /proc/cpuinfo': 'cpuinfo',
    'sudo fdisk -l': 'fdisk',
    'ifconfig': 'ifconfig',
    'lsblk -bPo NAME,FSTYPE,LABEL,UUID,MOUNTPOINT,TYPE,SIZE': 'lsblk',
    'cat /proc/meminfo | grep MemTotal:': 'meminfo',
    'cat /etc/os-release': 'os-release',
    'route -n': 'route',
    'hostname': 'hostname',
    'lsblk -no NAME': 'lsblkl',
}

UBUNTU_12_04 = RemoteHostMock.create_from_file(COMMANDS_OUTPUT_ROOT_DIRECTORY_PATH, 'ubuntu-12.04', COMMAND_DIRECTORY_MAP, {
    'block_devices': {
        'vda': {
            'type': 'disk',
            'fs': '',
            'uuid': '',
            'label': '',
            'mountpoint': '',
            'size': 10737418240,
            'children': {
                'vda1': {
                    'type': 'part',
                    'fs': 'ext4',
                    'uuid': 'fbea8976-8be3-475d-a97b-9507ff21be36',
                    'label': '',
                    'mountpoint': '/',
                    'size': 8588886016,
                    'start': 2048,
                    'end': 16777215,
                    'bootable': True,
                    'children': {},
                },
                'vda2': {
                    'type': 'part',
                    'fs': 'swap',
                    'uuid': '9b75df97-41ff-4475-b753-24584671b2b2',
                    'label': '',
                    'mountpoint': '[SWAP]',
                    'size': 2147483648,
                    'start': 16777216,
                    'end': 20971519,
                    'bootable': False,
                    'children': {},
                }
            }
        }
    },
    'network': {
        'hostname': 'ubuntu12',
        'interfaces' : {
            'lo': {
                'ip': '127.0.0.1',
                'net_mask': '255.0.0.0',
                'routes': []
            },
            'eth0': {
                'ip': '10.17.32.6',
                'net_mask': '255.255.255.0',
                'routes': [
                    {
                        'net': '0.0.0.0',
                        'gateway': '10.17.32.1',
                        'net_mask': '0.0.0.0'
                    },
                    {
                        'net': '10.17.32.0',
                        'gateway': '0.0.0.0',
                        'net_mask': '255.255.255.0'
                    }
                ]
            }
        }
    },
    'os': {
        'name': 'Ubuntu',
        'version': '12.04'
    },
    'hardware': {
        'ram': {
            'size': 1010504000
        },
        'cpus': [
            {
                'model': 'AMD Opteron 62xx class CPU',
                'mhz': 2799.948
            },
            {
                'model': 'AMD Opteron 62xx class CPU',
                'mhz': 2799.948
            },
            {
                'model': 'AMD Opteron 62xx class CPU',
                'mhz': 2799.948
            },
        ]
    }
})

UBUNTU_14_04 = RemoteHostMock.create_from_file(COMMANDS_OUTPUT_ROOT_DIRECTORY_PATH, 'ubuntu-14.04', COMMAND_DIRECTORY_MAP, {
    'block_devices': {
        'sda': {
            'type': 'disk',
            'fs': '',
            'uuid': '',
            'label': '',
            'mountpoint': '',
            'size': 42949672960,
            'children': {
                'sda1': {
                    'type': 'part',
                    'fs': 'ext4',
                    'uuid': '53baba04-22c7-4928-94d5-34f5737c025b',
                    'label': 'cloudimg-rootfs',
                    'mountpoint': '/',
                    'size': 42948624384,
                    'start': 2048,
                    'end': 83886079,
                    'bootable': True,
                    'children': {},
                },
            },
        },
        'sdb': {
            'type': 'disk',
            'fs': '',
            'uuid': '',
            'label': '',
            'mountpoint': '',
            'size': 5368709120,
            'children': {},
        }
    },
    'network': {
        'hostname': 'ubuntu14',
        'interfaces' : {
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
    },
    'os': {
        'name': 'Ubuntu',
        'version': '14.04'
    },
    'hardware': {
        'ram': {
            'size': 1017796000
        },
        'cpus': [
            {
                'model': 'Intel(R) Core(TM) i7-5557U CPU @ 3.10GHz',
                'mhz': 3099.790
            }
        ]
    }
})

UBUNTU_16_04 = RemoteHostMock.create_from_file(COMMANDS_OUTPUT_ROOT_DIRECTORY_PATH, 'ubuntu-16.04', COMMAND_DIRECTORY_MAP, {
    'block_devices': {
        'vda': {
            'type': 'disk',
            'fs': '',
            'uuid': '',
            'label': '',
            'mountpoint': '',
            'size': 10737418240,
            'children': {
                'vda1': {
                    'type': 'part',
                    'fs': 'ext4',
                    'uuid': '549c8755-2757-446e-8c78-f76b50491f21',
                    'label': '',
                    'mountpoint': '/',
                    'size': 10736369664,
                    'start': 2048,
                    'end': 20971519,
                    'bootable': True,
                    'children': {},
                },
            },
        },
        'vdb': {
            'type': 'disk',
            'fs': '',
            'uuid': '',
            'label': '',
            'mountpoint': '',
            'size': 10737418240,
            'children': {
                'vdb1': {
                    'type': 'part',
                    'fs': 'LVM2_member',
                    'uuid': '25fyrr-TMlE-KoqC-mlFS-BHtQ-oSat-orQK1v',
                    'label': '',
                    'mountpoint': '',
                    'size': 10736369664,
                    'bootable': False,
                    'start': 2048,
                    'end': 20971519,
                    'children': {
                        'vol1-lvol1': {
                            'type': 'lvm',
                            'fs': '',
                            'uuid': '',
                            'label': '',
                            'mountpoint': '',
                            'size': 83886080,
                            'children': {},
                        },
                    },
                },
            },
        },
        'vdc': {
            'type': 'disk',
            'fs': '',
            'uuid': '',
            'label': '',
            'mountpoint': '',
            'size': 10737418240,
            'children': {
                'vdc1': {
                    'type': 'part',
                    'fs': 'ext4',
                    'uuid': 'f52fdfe8-d862-44f9-b9b7-e35c0ada68cf',
                    'label': '',
                    'mountpoint': '',
                    'size': 5368709120,
                    'start': 2048,
                    'end': 10487807,
                    'bootable': False,
                    'children': {},
                },
                'vdc2': {
                    'type': 'part',
                    'fs': '',
                    'uuid': '',
                    'label': '',
                    'mountpoint': '',
                    'size': 5367660544,
                    'start': 10487808,
                    'end': 20971519,
                    'bootable': False,
                    'children': {},
                },
            }
        },
    },
    'network': {
        'hostname': 'ubuntu16',
        'interfaces' : {
            'lo': {
                'ip': '127.0.0.1',
                'net_mask': '255.0.0.0',
                'routes': []
            },
            'eth0': {
                'ip': '10.17.32.4',
                'net_mask': '255.255.255.0',
                'routes': [
                    {
                        'net': '0.0.0.0',
                        'gateway': '10.17.32.1',
                        'net_mask': '0.0.0.0',
                    },
                    {
                        'net': '10.0.0.0',
                        'gateway': '10.17.32.1',
                        'net_mask': '255.0.0.0',
                    },
                    {
                        'net': '10.17.32.0',
                        'gateway': '0.0.0.0',
                        'net_mask': '255.255.255.0',
                    },
                ]
            },
        }
    },
    'os': {
        'name': 'Ubuntu',
        'version': '16.04'
    },
    'hardware': {
        'ram': {
            'size': 1007264000
        },
        'cpus': [
            {
                'model': 'AMD Opteron 62xx class CPU',
                'mhz': 2799.980
            }
        ]
    }
})

TARGET__DEVICE_IDENTIFICATION = RemoteHostMock.create_from_file(
    COMMANDS_OUTPUT_ROOT_DIRECTORY_PATH,
    'target__device_identification',
    COMMAND_DIRECTORY_MAP,
    {
        'block_devices': {
            'vda': {
                'type': 'disk',
                'fs': '',
                'uuid': '',
                'label': '',
                'mountpoint': '',
                'size': 10737418240,
                'children': {
                    'vda1': {
                        'type': 'part',
                        'fs': 'ext4',
                        'uuid': '549c8755-2757-446e-8c78-f76b50491f21',
                        'label': '',
                        'mountpoint': '/',
                        'size': 3219128320,
                        'bootable': True,
                        'start': 2048,
                        'end': 6289407,
                        'children': {}
                    }
                }
            },
            'vdb': {
                'type': 'disk',
                'fs': '',
                'uuid': '',
                'label': '',
                'mountpoint': '',
                'size': 10737418240,
                'children': {}
            },
            'vdc': {
                'type': 'disk',
                'fs': '',
                'uuid': '',
                'label': '',
                'mountpoint': '',
                'size': 10737418240,
                'children': {}
            },
            'vdd': {
                'type': 'disk',
                'fs': '',
                'uuid': '',
                'label': '',
                'mountpoint': '',
                'size': 10737418240,
                'children': {}
            }
        },
        'network': {
            'hostname': 'template-jdepoix.smedia.pb-4.smhss.de',
            'interfaces': {
                'eth0': {
                    'ip': '10.17.32.15',
                    'net_mask': '255.255.255.0',
                    'routes': [
                        {
                            'net': '0.0.0.0',
                            'gateway': '10.17.32.1',
                            'net_mask': '0.0.0.0'
                        },
                        {
                            'net': '10.0.0.0',
                            'gateway': '10.17.32.1',
                            'net_mask': '255.0.0.0'
                        },
                        {
                            'net': '10.17.32.0',
                            'gateway': '0.0.0.0',
                            'net_mask': '255.255.255.0'
                        }
                    ]
                },
                'lo': {
                    'ip': '127.0.0.1',
                    'net_mask': '255.0.0.0',
                    'routes': []
                }
            }
        },
        'os': {
            'name': 'Ubuntu',
            'version': '16.04'
        },
        'hardware': {
            'cpus': [
                {
                    'model': 'AMD Opteron 62xx class CPU',
                    'mhz': 2799.998
                }
            ],
            'ram': {
                'size': 1007256000
            }
        }
    }
)
