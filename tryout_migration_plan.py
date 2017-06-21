MIGRATION_PLAN = {
    # This sections defines the blueprints. A blueprint is a document, which provides the information, which is needed
    # to migrate a given machine to the cloud. Here you can define in a more abstract way, how stuff is supposed to work
    # during the migration and then decide which source should use this blueprint, later on.
    "blueprints": {
        "default": {
            # blueprints can inherit from each other, by adding the following key-value pair to this blueprint dict.
            # "parent": "name-of-parent-blueprint"

            # in this section you provide information which is needed by the management server, to be able to ssh into
            # the source machines, which use this blueprint. All the properties here are optional and most are commented
            # out in this example, but feel free to use them as needed.
            "ssh": {
                "username": "user-to-log-in-with",
                # "private_key": "xxxxx",
                # "password": "xxxxxx",
                # These are the defaults, therefore they're not needed
                # "private_key_file_path": "~/.ssh/id_rsa_source",
                # "port": 22
            },
            # This sections defines, how ips will be assigned to the target machines as they are being created. By
            # defining this in an abstract mapping, you don't have to explicitly tell every interface, which ip it
            # should be assigned to, at the target location. You can still do that explicitly in the 'sources' section,
            # if you want to.
            "network_mapping": {
                # the key is the network the source machine is coming from and the value is the network the
                # corresponding network interface on the target machine, will be assigned to.
                "0.0.0.0/0": {
                    # This is the ID of the network the network interface of the target machine will be assigned to.
                    # How the ips are distributed inside this network, is defined in the 'target_cloud.networks' section
                    # below.
                    "network": "LAN 1",
                },
                "10.4.32.0/22": {
                    "network": "LAN 3",
                    # A range in which the IPs are distributed can be defined.
                    "range": {
                        "from": "10.17.32.100",
                        "to": "10.17.32.150"
                    }
                    # If you'd rather assign a static IP, you could do so, by using this instead of range:
                    # "static": "10.17.32.200"
                },
            },
            # In this section, hooks are defined, which are executed at a given lifecycle of the migration process.
            # The key is the name of the lifecycle, the hook is executed at. A lifecycle can either be suffixed with
            # "{lifecycle_name}_BEFORE" or "{lifecycle_name}_AFTER", indicating whether the hook is executed before
            # the lifecycle starts, or after it has finished. The following lifecycle are available and executed in this
            # order:
            #
            # DRAFT
            #   -> The source has just been parsed by the migration plan parser. Nothing really has happened yet.
            # CREATE_TARGET
            #   -> The target is created in the cloud.
            # GET_TARGET_SYSTEM_INFORMATION
            #   -> System information is retrieved from the newly created target machine.
            # IDENTIFY_DEVICES
            #   -> A mapping between the devices on the source and target machine is created.
            # CREATE_PARTITIONS
            #   -> The partitions are being replicated on the target machine, as they exist on the source machine.
            # CREATE_FILESYSTEMS
            #   -> The filesystems are being replicated on the target machine, as they exist on the source machine.
            # MOUNT_FILESYSTEMS
            #   -> The filesystems which have been created in the previous step, are being mounted
            # SYNC
            #   -> The actual sync is going on
            # FINAL_SYNC
            #   -> Another final sync before everything is getting ready for going live
            # ADJUST_NETWORK_CONFIG
            #   -> The network settings are being adjusted
            # ADJUST_SSH_CONFIG
            #   -> The ssh settings are being adjusted, to make sure a wrong ssh listen address, won't lock you out of
            #      the machine
            # ADJUST_FSTAB
            #   -> The /etc/fstab is being adjusted, to make sure booting is still possible after migration
            # REINSTALL_BOOTLOADER
            #   -> The bootloader will be reinstalled. This happens, while being chrooted in the final target
            #      environment
            # STOP_TARGET
            #   -> The target is being stopped
            # DELETE_BOOTSTRAP_VOLUME
            #   -> The bootstrap volume is being deleted
            # DELETE_BOOTSTRAP_NETWORK_INTERFACE
            #   -> The bootstrap network interface is being deleted
            # CONFIGURE_BOOT_DEVICE
            #   -> The new boot device will be set in the cloud
            # START_TARGET
            #   -> The Target will be started again and boot into the live system
            #
            # During script execution you have access to a dict called CONTEXT, which provides information about the
            # current migration. You'll find an example of what the CONTEXT dict looks like, in the comments below this
            # migration plan, since it's quite large.
            "hooks": {
                "SYNC_BEFORE": {
                    # this is the name of a script file, located in 'test_scripts/'
                    "script": "example.py",
                    # This is the location the hook is executed in. This can either be TARGET or SOURCE.
                    "location": "TARGET"
                    # By default the hooks are not executed as sudo. You can execute a script as sudo, by adding this
                    # option:
                    # "sudo": True
                }
            },
            # These are commands which are executed during the migration process. You most likely won't have to change
            # any of these, unless you want to add another filesystem.
            "commands": {
                "create_filesystem": {
                    "ext4": {
                        "command": "sudo mkfs.ext4 {OPTIONALS} -F {DEVICE}",
                        "optionals": {
                            "uuid": "-U {UUID}",
                            "label": "-L {LABEL}"
                        }
                    },
                    "ext3": {
                        "command": "sudo mkfs.ext3 {OPTIONALS} -F {DEVICE}",
                        "optionals": {
                            "uuid": "-U {UUID}",
                            "label": "-L {LABEL}"
                        }
                    },
                    "ext2": {
                        "command": "sudo mkfs.ext2 {OPTIONALS} -F {DEVICE}",
                        "optionals": {
                            "uuid": "-U {UUID}",
                            "label": "-L {LABEL}"
                        }
                    }
                },
                "sync": "sudo rsync -zaXAPx --delete --numeric-ids -e \"ssh -i $HOME/.ssh/id_rsa -o StrictHostKeyChecking=no\" --rsync-path=\"sudo rsync\" {SOURCE_DIR}/ {TARGET_DIR}",
                "reinstall_bootloader": "sudo grub-install --boot-directory=/boot {DEVICE}",
            }
        }
    },
    # This is the list of sources which will be migrated. Please keep in mind, that scheduling is not implemented yet
    # and therefore only the first source will be migrated, when the migration script is started.
    "sources": [
        {
            # The address of the source system
            "address": "10.4.33.14",
            # The blueprint which should be used, to migrate this source
            "blueprint": "default"
            # You could also define another blueprint inline, to define something specifically for this source.
            # For example if you would like to give this source a static ip, but use the default blueprint besides that
            # you could do this:
            #
            # "blueprint": {
            #     "parent": "default",
            #     "network_mapping": {
            #         "192.168.0.0/24": {
            #             "network": "LAN 2",
            #             "static": "10.17.32.100"
            #         }
            #     }
            # }
        }
    ],
    # This section contains information relevant for the creation of the target machine in the cloud
    "target_cloud": {
        # This only indicates, that the cloud you are migrating to is profitbricks. So this is not relevant as long as
        # only profitbricks is supported
        "provider": "PB",
        # The id of the datacenter you want to migrate to
        "datacenter": "xxxxxx-xxxxxx-xxxxxxx-xxxxxxx",
        "login": {
            # the login credentials used for the profitbricks API
            "username": "user@mail.net",
            "password": "xxxxxxxxxxxxxx"
        },
        # information relevant for creating the bootstrapping machine
        "bootstrapping": {
            # the id of the template which is used to create the bootstrapping image
            "template_id": "410a9719-b273-4251-b3dd-a63ea75f7218",
            # the size of the bootstrapping volume
            "size": 10,
            # the ssh credentials needed to get into the bootstrapping system
            "ssh": {
                "username": "jdepoix"
            },
            # the network the bootstrapping network interface should be assigned to
            "network": {
                "network": "LAN 3",
                "range": {
                    "from": "10.17.32.50",
                    "to": "10.17.32.90"
                }
            }
        },
        # In this section the networks are defined, which are referenced in the blueprints
        "networks": {
            # The key is the name of the network, which it will be referenced by, in the context of the blueprints
            "LAN 1": {
                # the id of the network in the cloud
                "cloud_id": "1",
                # its netaddress
                "net": "0.0.0.0/0",
            },
            "LAN 3": {
                "cloud_id": "3",
                "net": "10.17.32.0/24",
                "gateway": "10.17.32.1",
            }
        },
    },
    # Information about the migration process. This is not relevant as long scheduling is not implemented.
    "migration": {
        "simultaneous_migrations": 10,
        "minutes_between_syncs": 120
    }
}

# This is what the context dict looks like, during script execution. It mainly divides into the following sections:
# - blueprint
#   the resolved blueprint, this machine is following
#
# - target_system_info
#   system information about the target machine
#
# - source_system_info
#   system information about the source machine
#
# - cloud_metadata
#   information about returned by the cloud, as the target machine was created. You can find the IPs here and stuff like
#   that
#
# - device_mapping
#   this tells you, on which device, the devices from the source machine are mapped to, on the target machine and what
#   the mountpoint is, they are mounted on during migration
#
# CONTEXT = {
#     'blueprint':
#         {
#             'hooks': {
#                 'SYNC_BEFORE': {
#                     'execute': "with open('context_dump.txt', 'w+') as file:\n    # during execution CONTEXT will contain information about the migration, which should help writing more useful\n    # scripts\n    file.write(str(CONTEXT))\n",
#                     'location': 'TARGET',
#                      'script': 'example.py'
#                 }
#             },
#             'commands': {
#                 'create_filesystem': {
#                     'ext4': {
#                         'command': 'sudo mkfs.ext4 {OPTIONALS} -F {DEVICE}',
#                         'optionals': {
#                             'uuid': '-U {UUID}',
#                             'label': '-L {LABEL}'
#                         }
#                     },
#                     'ext3': {
#                         'command': 'sudo mkfs.ext3 {OPTIONALS} -F {DEVICE}',
#                         'optionals': {
#                             'uuid': '-U {UUID}',
#                             'label': '-L {LABEL}'
#                         }
#                     },
#                     'ext2': {
#                         'command': 'sudo mkfs.ext2 {OPTIONALS} -F {DEVICE}',
#                         'optionals': {
#                             'uuid': '-U {UUID}',
#                             'label': '-L {LABEL}'
#                         }
#                     }
#                 },
#                 'sync': 'sudo rsync -zaXAPx --delete --numeric-ids -e "ssh -i $HOME/.ssh/id_rsa -o StrictHostKeyChecking=no" --rsync-path="sudo rsync" {SOURCE_DIR}/ {TARGET_DIR}',
#                 'reinstall_bootloader': 'sudo grub-install --boot-directory=/boot {DEVICE}'
#             },
#             'network_interfaces': [
#                 {
#                     'network_id': 'LAN 3',
#                     'ip': '10.17.32.100',
#                     'net_mask': '255.255.255.0',
#                     'gateway': '10.17.32.1',
#                     'source_interface': 'eth0'
#                 },
#                 {
#                     'network_id': 'LAN 1',
#                     'ip': None,
#                     'net_mask': None,
#                     'gateway': None,
#                     'source_interface': 'eth1'
#                 }
#             ],
#             'ssh': {
#                 'username': 'jdepoix'
#             },
#             'bootstrapping_network_interface': {
#                 'network_id': 'LAN 3',
#                 'ip': '10.17.32.50',
#                 'net_mask': '255.255.255.0',
#                 'gateway': '10.17.32.1'
#             }
#         },
#     'target_system_info': {
#         'hardware': {
#             'ram': {
#                 'size': 2555576000
#             },
#             'cpus': [
#                 {
#                     'model': 'AMD Opteron 62xx class CPU',
#                     'mhz': 2799.95
#                 },
#                 {
#                     'model': 'AMD Opteron 62xx class CPU',
#                     'mhz': 2799.95
#                 }
#             ]
#         },
#         'block_devices': {
#             'vda': {
#                 'fs': '',
#                 'uuid': '',
#                 'label': '',
#                 'mountpoint': '',
#                 'type': 'disk',
#                 'children': {
#                     'vda1': {
#                         'start': 2048,
#                         'fs': 'ext4',
#                         'end': 6289407,
#                         'uuid': '549c8755-2757-446e-8c78-f76b50491f21',
#                         'bootable': True,
#                         'mountpoint': '/',
#                         'size': 3219128320,
#                         'type': 'part',
#                         'children': {},
#                         'label': ''
#                     }
#                 },
#                 'size': 10737418240
#             },
#             'vdc': {
#                 'fs': '',
#                 'uuid': '',
#                 'label': '',
#                 'mountpoint': '',
#                 'type': 'disk',
#                 'children': {
#                     'vdc1': {
#                         'start': 1,
#                         'fs': 'ext4',
#                         'end': 10474379,
#                         'uuid': '002a5a59-7f75-493f-aeb2-0defe3ce9d30',
#                         'bootable': False,
#                         'mountpoint': '/mnt/11818500112226228047',
#                         'size': 5362882048,
#                         'type': 'part',
#                         'children': {},
#                         'label': ''
#                     }
#                 },
#                 'size': 5368709120
#             },
#             'vdb': {
#                 'fs': '',
#                 'uuid': '',
#                 'label': '',
#                 'mountpoint': '',
#                 'type': 'disk',
#                 'children': {
#                     'vdb5': {
#                         'start': 501760,
#                         'fs': '',
#                         'end': 2500607,
#                         'uuid': '',
#                         'bootable': False,
#                         'mountpoint': '',
#                         'size': 1023410176,
#                         'type': 'part',
#                         'children': {},
#                         'label': ''
#                     },
#                     'vdb6': {
#                         'start': 2502656,
#                         'fs': 'ext4',
#                         'end': 16775167,
#                         'uuid': '2d56f0eb-0542-4dee-b46c-af7b5c6ebf78',
#                         'bootable': False,
#                         'mountpoint': '/mnt/13689863022826529725',
#                         'size': 7307526144,
#                         'type': 'part',
#                         'children': {},
#                         'label': ''
#                     },
#                     'vdb1': {
#                         'start': 2048,
#                         'fs': 'ext2',
#                         'end': 499711,
#                         'uuid': '0ab6c82b-3302-4daa-9883-1db7fedc18d9',
#                         'bootable': False,
#                         'mountpoint': '/mnt/444137628937237450',
#                         'size': 254803968,
#                         'type': 'part',
#                         'children': {},
#                         'label': ''
#                     },
#                     'vdb2': {
#                         'start': 501758,
#                         'fs': '',
#                         'end': 16775167,
#                         'uuid': '',
#                         'bootable': False,
#                         'mountpoint': '',
#                         'size': 1024,
#                         'type': 'part',
#                         'children': {},
#                         'label': ''
#                     }
#                 },
#                 'size': 8589934592
#             },
#             'vdd': {
#                 'fs': '',
#                 'uuid': '',
#                 'label': '',
#                 'mountpoint': '',
#                 'type': 'disk',
#                 'children': {
#                     'vdd1': {
#                         'start': 1,
#                         'fs': 'ext4',
#                         'end': 62910539,
#                         'uuid': '4ce1594f-4d7d-4f29-b9eb-3af86fcd1561',
#                         'bootable': False,
#                         'mountpoint': '/mnt/1330379168980705430',
#                         'size': 32210195968,
#                         'type': 'part',
#                         'children': {},
#                         'label': ''
#                     }
#                 },
#                 'size': 32212254720
#             }
#         },
#         'os': {
#             'version': '16.04',
#             'name': 'Ubuntu'
#         },
#         'network': {
#             'interfaces': {
#                 'lo': {
#                     'routes': [],
#                     'ip': '127.0.0.1',
#                     'net_mask': '255.0.0.0'
#                 },
#                 'eth0': {
#                     'routes': [
#                         {
#                             'net': '0.0.0.0',
#                             'net_mask': '0.0.0.0',
#                             'gateway': '10.17.32.1'
#                         },
#                         {
#                             'net': '10.0.0.0',
#                             'net_mask': '255.0.0.0',
#                             'gateway': '10.17.32.1'
#                         },
#                         {
#                             'net': '10.17.32.0',
#                             'net_mask': '255.255.255.0',
#                             'gateway': '0.0.0.0'
#                         }
#                     ],
#                     'ip': '10.17.32.50',
#                     'net_mask': '255.255.255.0'
#                 }
#             },
#             'hostname': 'template-jdepoix.smedia.pb-4.smhss.de'
#         }
#     },
#     'cloud_metadata': {
#         'network_interfaces': [
#             {
#                 'ip': '185.48.116.97',
#                 'lan': 1,
#                 'id': '59f18030-a6e0-4f4e-8cdf-a17bead8c79f',
#                 'name': None
#             },
#             {
#                 'ip': '10.17.32.100',
#                 'lan': 3,
#                 'id': '61b76115-9fbb-491e-9005-5112683fbf79',
#                 'name': None
#             },
#             {
#                 'ip': '10.17.32.50',
#                 'lan': 3,
#                 'id': '2008a981-1e30-4053-af7b-0fa085cf0068',
#                 'name': 'confluence-3905.swift.fra-1.smhss.de.bootstrap'
#             }
#         ],
#         'id': '67893844-3670-4779-9f53-156ffe3f208a',
#         'volumes': [
#             {
#                 'size': 10,
#                 'id': '724547bc-1de5-42b0-ae2f-0242ae1cca0c',
#                 'name': 'confluence-3905.swift.fra-1.smhss.de.bootstrap',
#                 'device_number': 1
#             },
#             {
#                 'size': 8,
#                 'id': '8e98c761-92e1-40c3-9bdf-e954c1e99ac8',
#                 'name': 'confluence-3905.swift.fra-1.smhss.de.clone-0',
#                 'device_number': 2
#             },
#             {
#                 'size': 30, 'id': 'd0d732e2-1503-4b95-8ea0-980a62af21b9',
#                 'name': 'confluence-3905.swift.fra-1.smhss.de.clone-2',
#                 'device_number': 4
#             },
#             {
#                 'size': 5,
#                 'id': '0f1824c2-3bc0-4768-87ca-4a4264b7572f',
#                 'name': 'confluence-3905.swift.fra-1.smhss.de.clone-1',
#                 'device_number': 3
#             }
#         ]
#     },
#     'source_system_info': {
#         'hardware': {
#             'ram': {
#                 'size': 2557180000
#             },
#             'cpus': [
#                 {
#                     'model': 'Intel(R) Xeon(R) CPU E5-2680 v3 @ 2.50GHz', 'mhz': 2500.042
#                 },
#                 {
#                     'model': 'Intel(R) Xeon(R) CPU E5-2680 v3 @ 2.50GHz', 'mhz': 2500.042
#                 }
#             ]
#         },
#         'block_devices': {
#             'xvdb': {
#                 'fs': '',
#                 'uuid': '',
#                 'label': '',
#                 'mountpoint': '',
#                 'type': 'disk',
#                 'children': {
#                     'xvdb1': {
#                         'start': 1,
#                         'fs': 'ext4',
#                         'end': 10474379,
#                         'uuid': '002a5a59-7f75-493f-aeb2-0defe3ce9d30',
#                         'bootable': False,
#                         'mountpoint': '/opt/confluence',
#                         'label': '',
#                         'type': 'part',
#                         'children': {},
#                         'size': 5362882048
#                     }
#                 },
#                 'size': 5368709120
#             },
#             'xvdc': {
#                 'fs': '',
#                 'uuid': '',
#                 'label': '',
#                 'mountpoint': '',
#                 'type': 'disk',
#                 'children': {
#                     'xvdc1': {
#                         'start': 1,
#                         'fs': 'ext4',
#                         'end': 62910539,
#                         'uuid': '4ce1594f-4d7d-4f29-b9eb-3af86fcd1561',
#                         'bootable': False,
#                         'mountpoint': '/mnt/data',
#                         'label': '',
#                         'type': 'part',
#                         'children': {},
#                         'size': 32210195968
#                     }
#                 },
#                 'size': 32212254720
#             },
#             'xvda': {
#                 'fs': '',
#                 'uuid': '',
#                 'label': '',
#                 'mountpoint': '',
#                 'type': 'disk',
#                 'children': {
#                     'xvda5': {
#                         'start': 501760,
#                         'fs': 'swap',
#                         'end': 2500607,
#                         'uuid': 'a6741189-d0c6-438c-b18a-779d45318a5f',
#                         'bootable': False,
#                         'mountpoint': '[SWAP]',
#                         'label': '',
#                         'type': 'part',
#                         'children': {},
#                         'size': 1023410176
#                     },
#                     'xvda6': {
#                         'start': 2502656,
#                         'fs': 'ext4',
#                         'end': 16775167,
#                         'uuid': '2d56f0eb-0542-4dee-b46c-af7b5c6ebf78',
#                         'bootable': False,
#                         'mountpoint': '/',
#                         'label': '',
#                         'type': 'part',
#                         'children': {},
#                         'size': 7307526144
#                     },
#                     'xvda1': {
#                         'start': 2048,
#                         'fs': 'ext2',
#                         'end': 499711,
#                         'uuid': '0ab6c82b-3302-4daa-9883-1db7fedc18d9',
#                         'bootable': False,
#                         'mountpoint': '/boot',
#                         'label': '',
#                         'type': 'part',
#                         'children': {},
#                         'size': 254803968
#                     },
#                     'xvda2': {
#                         'start': 501758,
#                         'fs': '',
#                         'end': 16775167,
#                         'uuid': '',
#                         'bootable': False,
#                         'mountpoint': '',
#                         'label': '',
#                         'type': 'part',
#                         'children': {},
#                         'size': 1024
#                     }
#                 },
#                 'size': 8589934592
#             }
#         },
#         'os': {
#             'version': '12.04',
#             'name': 'Ubuntu'
#         },
#         'network': {
#             'interfaces': {
#                 'lo': {
#                     'routes': [],
#                     'ip': '127.0.0.1',
#                     'net_mask': '255.0.0.0'
#                 },
#                 'eth1': {
#                     'routes': [
#                         {
#                             'net': '0.0.0.0',
#                             'net_mask': '0.0.0.0',
#                             'gateway': '185.122.181.1'
#                         },
#                         {
#                             'net': '185.122.181.0',
#                             'net_mask': '255.255.255.0',
#                             'gateway': '0.0.0.0'
#                         }
#                     ],
#                     'ip': '185.122.181.169',
#                     'net_mask': '255.255.255.0'
#                 },
#                 'eth0': {
#                     'routes':
#                         [
#                             {
#                                 'net': '10.0.0.0',
#                                 'net_mask': '255.0.0.0',
#                                 'gateway': '10.4.32.172'
#                             },
#                             {
#                                 'net': '10.4.32.0',
#                                 'net_mask': '255.255.252.0',
#                                 'gateway': '0.0.0.0'
#                             }
#                         ],
#                     'ip': '10.4.33.14',
#                     'net_mask': '255.255.252.0'
#                 }
#             },
#             'hostname': 'confluence-3905.swift.fra-1.smhss.de'
#         }
#     },
#     'device_mapping': {
#         'xvdb': {
#             'mountpoint': '',
#             'id': 'vdc',
#             'children': {
#                 'xvdb1': {
#                     'mountpoint': '/mnt/11818500112226228047',
#                     'id': 'vdc1'
#                 }
#             }
#         },
#         'xvdc': {
#             'mountpoint': '',
#             'id': 'vdd',
#             'children': {
#                 'xvdc1': {
#                     'mountpoint': '/mnt/1330379168980705430',
#                     'id': 'vdd1'}
#             }
#         },
#         'xvda': {
#             'mountpoint': '',
#             'id': 'vdb',
#             'children': {
#                 'xvda5': {
#                     'mountpoint': '',
#                     'id': 'vdb5'
#                 },
#                 'xvda6': {
#                     'mountpoint': '/mnt/13689863022826529725',
#                     'id': 'vdb6'
#                 },
#                 'xvda1': {
#                     'mountpoint': '/mnt/444137628937237450',
#                     'id': 'vdb1'
#                 },
#                 'xvda2': {
#                     'mountpoint': '', 'id': 'vdb2'
#                 }
#             }
#         }
#     }
# }