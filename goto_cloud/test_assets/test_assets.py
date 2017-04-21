from .remote_host_patch_metaclass import PatchRemoteHostMeta
from .remote_host_mocks import UBUNTU_12_04, UBUNTU_14_04, UBUNTU_16_04, UBUNTU_16_04__LVM,\
    TARGET__DEVICE_IDENTIFICATION, TARGET__FILESYSTEM_CREATION
from .migration_plan_mock import MIGRATION_PLAN_MOCK


class TestAsset():
    PatchRemoteHostMeta = PatchRemoteHostMeta

    REMOTE_HOST_MOCKS = {
        'ubuntu12': UBUNTU_12_04,
        'ubuntu14': UBUNTU_14_04,
        'ubuntu16': UBUNTU_16_04,
        'ubuntu16__lvm': UBUNTU_16_04__LVM,
        'target__device_identification': TARGET__DEVICE_IDENTIFICATION,
        'target__filesystem_creation': TARGET__FILESYSTEM_CREATION
    }

    MIGRATION_PLAN_MOCK = MIGRATION_PLAN_MOCK
