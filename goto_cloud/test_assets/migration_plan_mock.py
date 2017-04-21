MIGRATION_PLAN_MOCK = {
    "blueprints": {
        "default": {
            "ssh": {
                "private_key": "xxxxx",
                "private_key_file_path": "~/.ssh/id_rsa_source",
                "username": "root",
                "password": "xxxxxx",
                "port": 22
            },
            "network_mapping": {
                "0.0.0.0/0": {
                    "network": "LAN 1",
                },
                "192.168.0.0/24": {
                    "network": "LAN 2",
                    "range": {
                        "from": "10.17.32.100",
                        "to": "10.17.32.200"
                    }
                },
                "192.168.10.0/24": {
                    "network": "LAN 3",
                    "range": {
                        "from": "10.17.33.100",
                        "to": "10.17.33.200"
                    }
                },
                "10.8.3.8.0/24": {
                    "network": "LAN 4",
                    "range": {
                        "from": "10.17.34.100",
                        "to": "10.17.34.200"
                    }
                },
            },
            "hooks": {
                "go_live_after": {
                    "location": "target",
                    "execute": "ls",
                }
            },
            "commands": {
                "create_filesystem": {
                    "ext4": {
                        "command": "sudo mkfs.ext4 {OPTIONALS} {DEVICE}",
                        "optionals": {
                            "uuid": "-u {UUID}",
                            "label": "-l {LABEL}"
                        }
                    },
                    "ext3": {
                        "command": "sudo mkfs.ext3 {OPTIONALS} {DEVICE}",
                        "optionals": {
                            "uuid": "-u {UUID}",
                            "label": "-l {LABEL}"
                        }
                    }
                },
                "sync": "sudo rsync -zaXAPx --delete --numeric-ids -e ssh {SOURCE_DIR} {TARGET_DIR}",
                "reinstall_bootloader": "sudo grub-install --boot-directory=/boot {DEVICE}",
                "create_partition": "echo -e \"n\n\n{PARTITION_NUMBER}\n{START}\n{END}\nw\n\" | sudo fdisk {DEVICE}",
                "tag_partition_bootable": {
                    "command": "echo -e \"a\n{OPTIONALS}w\n\" | sudo fdisk {PARENT_DEVICE}",
                    "optionals": {
                        "partition_number": "{PARTITION_NUMBER}\n"
                    }
                }
            }
        },
        "django": {
            "parent": "default",
            "hooks": {
                "go_live_before": {
                    "location": "target",
                    "execute": "systemctl stop nginx gunicorn celery-main celery-beat",
                },
                "go_live_after": {
                    "location": "target",
                    "execute": "systemctl start nginx gunicorn celery-main celery-beat",
                }
            },
            "hardware": {
                "cores": 2,
                "ram": 4,
            }
        }
    },
    "sources": [
        {
            "address": "ubuntu12",
            "blueprint": "default"
        },
        {
            "address": "ubuntu14",
            "blueprint": {
                "parent": "django",
                "network_mapping": {
                    "192.168.0.0/24": {
                        "network": "LAN 2",
                        "range": {
                            "from": "10.17.32.10",
                            "to": "10.17.32.30"
                        }
                    }
                }
            }
        },
        {
            "address": "ubuntu16",
            "blueprint": {
                "parent": "django",
                "network_mapping": {
                    "192.168.0.0/24": {
                        "network": "LAN 2",
                        "static": "10.17.32.100"
                    }
                }
            }
        },
        {
            "address": "ubuntu16__lvm",
            "blueprint": "default"
        }
    ],
    "target_cloud": {
        "platform": "pb",
        "datacenter": "pb-4",
        "login": {
            "username": "devnull@seibert-media.net",
            "password": "xxxxxxxxxx"
        },
        "bootstrapping": {
            "template_snapshot": "template_bootstrap_vm",
            "ssh": {
                "private_key": "xxxxx",
                "private_key_file_path": "~/.ssh/id_rsa_source",
                "username": "root",
                "password": "xxxxxx",
                "port": 22
            },
            "network": "LAN 0"
        },
        "networks": {
            "LAN 1": {
                "net": "0.0.0.0/0",
            },
            "LAN 2": {
                "net": "10.17.32.0/24",
                "gateway": "10.17.32.1",
            },
            "LAN 3": {
                "net": "10.17.33.0/24",
                "gateway": "10.17.33.1",
            },
            "LAN 4": {
                "net": "10.17.34.0/24",
                "gateway": "10.17.34.1",
            }
        },
    },
    "migration": {
        "simultaneous_migrations": 10,
        "minutes_between_syncs": 120
    }
}
