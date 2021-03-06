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
                    "192.168.0.0/24": {
                        "network": "LAN 2",
                        "range": {
                            "from": "10.17.32.10",
                            "to": "10.17.32.30"
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
                    },
                    "FINAL_SYNC_BEFORE": {
                        "execute": "with open('hook_was_executed.txt', 'w+') as f:\n\tf.write('was executed')",
                        "location": "SOURCE",
                    },
                    "FINAL_SYNC_AFTER": {
                        "execute": "with open('hook_was_executed.txt', 'w+') as f:\n\tf.write('was executed')",
                        "location": "SOURCE",
                    },
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
                        },
                    },
                    "sync":
                        "sudo rsync -zaXAPx --delete --numeric-ids "
                        "-e \"ssh -i $HOME/.ssh/id_rsa -o StrictHostKeyChecking=no\" "
                        "--rsync-path=\"sudo rsync\" {SOURCE_DIR}/ {TARGET_DIR}",
                    "reinstall_bootloader": "sudo grub-install --boot-directory=/boot {DEVICE}",
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
                        },
                    },
                    "sync":
                        "sudo rsync -zaXAPx --delete --numeric-ids "
                        "-e \"ssh -i $HOME/.ssh/id_rsa -o StrictHostKeyChecking=no\" "
                        "--rsync-path=\"sudo rsync\" {SOURCE_DIR}/ {TARGET_DIR}",
                    "reinstall_bootloader": "sudo grub-install --boot-directory=/boot {DEVICE}",
                }
            }
        )

    def test_resolve__invalid_parent_id(self):
        with self.assertRaises(BlueprintResolver.ResolvingException):
            self.blueprint_resolver.resolve("i_do_not_exist")

    def test_resolve__invalid_blueprint(self):
        with self.assertRaises(BlueprintResolver.ResolvingException):
            self.blueprint_resolver.resolve(123)
