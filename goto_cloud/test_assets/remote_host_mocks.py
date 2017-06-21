import os

from settings.base import BASE_DIR


class RemoteHostMock(object):
    def __init__(self, commands, expected_config):
        self.commands = commands
        self.expected_config = expected_config

    def execute(self, command):
        matching_commands = [known_command for known_command in self.commands if known_command in command]

        if matching_commands:
            return {
                'exit_code': 0,
                'stdout': self.commands[matching_commands[0]].strip() if self.commands[matching_commands[0]] else '',
                'stderr': '',
            }
        return {
            'exit_code': 1,
            'stdout': '',
            'stderr': 'Command {command_name} not known!'.format(command_name=command).encode(),
        }

    def get_config(self):
        return self.expected_config

    def add_command(self, command_name, command_output):
        self.commands[command_name] = command_output

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
            if command_directory_map[command]:
                with open(
                    os.path.join(os.path.join(commands_root_directory, command_directory_map[command]), filename)
                ) as command_output:
                    commands[command] = command_output.read()
            else:
                commands[command] = None

        return RemoteHostMock(commands, expected_config)


COMMANDS_OUTPUT_ROOT_DIRECTORY_PATH = BASE_DIR + '/test_assets/static_assets/test_vms_command_output'
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
    '| sudo fdisk': None,
    'sudo mkfs': None,
    'rsync': None,
    'mount': None,
    'grub-install': None,
    'echo -e': None,
    'mkdir': None,
    '(': None,
    '&': None,
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

UBUNTU_16_04__LVM = RemoteHostMock.create_from_file(
    COMMANDS_OUTPUT_ROOT_DIRECTORY_PATH,
    'ubuntu-16.04',
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
            'hostname': 'ubuntu16__lvm',
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
    }
)

UBUNTU_16_04 = RemoteHostMock.create_from_file(COMMANDS_OUTPUT_ROOT_DIRECTORY_PATH, 'ubuntu16__lvm', COMMAND_DIRECTORY_MAP, {
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
                    'bootable': True,
                    'start': 2048,
                    'end': 20971519,
                    'children': {}
                }
            }
        },
        'vdb': {
            'type': 'disk',
            'fs': 'ext3',
            'uuid': 'd04ba532-cd2d-4406-a5ef-114acf019cc8',
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
            'children': {
                'vdc1': {
                    'type': 'part',
                    'fs': 'ext4',
                    'uuid': '53ad2170-488d-481a-a6ab-5ce0e538f247',
                    'label': '',
                    'mountpoint': '/mnt/vdc1',
                    'size': 5368709120,
                    'bootable': False,
                    'start': 2048,
                    'end': 10487807,
                    'children': {}
                },
                'vdc2': {
                    'type': 'part',
                    'fs': 'ext4',
                    'uuid': 'bcab224c-8407-4783-8cea-f9ea4be3fabf',
                    'label': '',
                    'mountpoint': '/mnt/vdc2',
                    'size': 5367660544,
                    'bootable': False,
                    'start': 10487808,
                    'end': 20971519,
                    'children': {}
                }
            }
        },
    },
    'network': {
        'hostname': 'ubuntu16',
        'interfaces': {
            'eth0': {
                'ip': '10.17.32.4',
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
                'mhz': 2799.98
            }
        ],
        'ram': {
            'size': 1007168000
        }
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
            'hostname': 'target__device_identification',
            'interfaces': {
                'eth0': {
                    'ip': '10.17.32.15',
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

TARGET__FILESYSTEM_CREATION = RemoteHostMock.create_from_file(
    COMMANDS_OUTPUT_ROOT_DIRECTORY_PATH,
    'target__filesystem_creation',
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
                'children': {
                    'vdb1': {
                        'type': 'part',
                        'fs': '',
                        'uuid': '',
                        'label': '',
                        'mountpoint': '',
                        'size': 10736369664,
                        'bootable': True,
                        'start': 2048,
                        'end': 20971519,
                        'children': {}
                    }
                }
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
                'children': {
                    'vdd1': {
                        'type': 'part',
                        'fs': '',
                        'uuid': '',
                        'label': '',
                        'mountpoint': '',
                        'size': 5368709120,
                        'bootable': False,
                        'start': 2048,
                        'end': 10487807,
                        'children': {}
                    },
                    'vdd2': {
                        'type': 'part',
                        'fs': '',
                        'uuid': '',
                        'label': '',
                        'mountpoint': '',
                        'size': 5367660544,
                        'bootable': False,
                        'start': 10487808,
                        'end': 20971519,
                        'children': {}
                    }
                }
            },
        },
        'network': {
            'hostname': 'target__filesystem_creation',
            'interfaces': {
                'eth0': {
                    'ip': '10.17.32.15',
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
