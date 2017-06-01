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
                "192.168.33.0/24": {
                    "network": "LAN 3",
                    "range": {
                        "from": "10.17.33.100",
                        "to": "10.17.33.200"
                    }
                },
                "10.17.32.0/24": {
                    "network": "LAN 4",
                    "range": {
                        "from": "10.17.34.100",
                        "to": "10.17.34.200"
                    }
                },
                "10.0.2.0/24": {
                    "network": "LAN 4",
                    "range": {
                        "from": "10.17.34.10",
                        "to": "10.17.34.50"
                    }
                },
            },
            "hooks": {
                "SYNC_AFTER": {
                    "execute": "with open('hook_was_executed.txt', 'w+') as f:\n\tf.write('was executed')",
                    "location": "TARGET"
                }
            },
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
        },
        "django": {
            "parent": "default",
            "hooks": {
                "FINAL_SYNC_BEFORE": {
                    "execute": "with open('hook_was_executed.txt', 'w+') as f:\n\tf.write('was executed')",
                    "location": "SOURCE",
                },
                "FINAL_SYNC_AFTER": {
                    "execute": "with open('hook_was_executed.txt', 'w+') as f:\n\tf.write('was executed')",
                    "location": "SOURCE",
                },
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
        "provider": "PB",
        "datacenter": "pb-4",
        "login": {
            "username": "devnull@seibert-media.net",
            "password": "xxxxxxxxxx"
        },
        "bootstrapping": {
            "template_id": "template_bootstrap_vm",
            "size": 10,
            "ssh": {
                "private_key": "xxxxx",
                "private_key_file_path": "~/.ssh/id_rsa_source",
                "username": "root",
                "password": "xxxxxx",
                "port": 22
            },
            "network": "LAN 1"
        },
        "networks": {
            "LAN 1": {
                "cloud_id": "1",
                "net": "0.0.0.0/0",
            },
            "LAN 2": {
                "cloud_id": "2",
                "net": "10.17.32.0/24",
                "gateway": "10.17.32.1",
            },
            "LAN 3": {
                "cloud_id": "3",
                "net": "10.17.33.0/24",
                "gateway": "10.17.33.1",
            },
            "LAN 4": {
                "cloud_id": "4",
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
