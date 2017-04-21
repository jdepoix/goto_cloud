from unittest import TestCase

from test_assets.public import TestAsset

from ..blueprint_resolving import BlueprintResolver


class TestBlueprintResolver(TestCase):
    def setUp(self):
        self.blueprint_resolver = BlueprintResolver(TestAsset.MIGRATION_PLAN_MOCK['blueprints'])


    def test_resolve(self):
        self.assertDictEqual(
            self.blueprint_resolver.resolve(
                {
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
            ),
            {
                "ssh": {
                    "private_key": "xxxxx",
                    "private_key_file_path": "~/.ssh/id_rsa_source",
                    "username": "root",
                    "password": "xxxxxx",
                    "port": 22
                },
                "hardware": {
                    "cores": 2,
                    "ram": 4,
                },
                "network_mapping": {
                    "0.0.0.0/0": {
                        "network": "LAN 1",
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
                    "192.168.0.0/24": {
                        "network": "LAN 2",
                        "range": {
                            "from": "10.17.32.10",
                            "to": "10.17.32.30"
                        }
                    },
                },
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
            }
        )

    def test_resolve__by_id(self):
        self.assertDictEqual(
            self.blueprint_resolver.resolve("default"),
            {
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
            }
        )

    def test_resolve__invalid_parent_id(self):
        with self.assertRaises(BlueprintResolver.ResolvingException):
            self.blueprint_resolver.resolve("i_do_not_exist")

    def test_resolve__invalid_blueprint(self):
        with self.assertRaises(BlueprintResolver.ResolvingException):
            self.blueprint_resolver.resolve(123)
