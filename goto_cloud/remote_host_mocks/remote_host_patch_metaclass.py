from unittest.mock import patch

from .remote_host_mocks import UBUNTU_12_04, UBUNTU_14_04, UBUNTU_16_04, UBUNTU_16_04__LVM,\
    TARGET__DEVICE_IDENTIFICATION


class PatchRemoteHostMeta(type):
    """
    can be used as a metaclass for a TestCase to patch relevant methods, required to mock a RemoteHost
    """
    MOCKS = {
        'ubuntu12': UBUNTU_12_04,
        'ubuntu14': UBUNTU_14_04,
        'ubuntu16': UBUNTU_16_04,
        'ubuntu16__lvm': UBUNTU_16_04__LVM,
        'target__device_identification': TARGET__DEVICE_IDENTIFICATION,
    }

    MOCKED_EXECUTE = lambda remote_executor, command: PatchRemoteHostMeta.MOCKS[remote_executor.hostname].execute(
        command
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patch('remote_execution.remote_execution.SshRemoteExecutor.connect', lambda self: None)(self)
        patch('remote_execution.remote_execution.SshRemoteExecutor.close', lambda self: None)(self)
        patch('remote_execution.remote_execution.SshRemoteExecutor.is_connected', lambda self: True)(self)
        patch(
            'remote_execution.remote_execution.SshRemoteExecutor._execute',
            PatchRemoteHostMeta.MOCKED_EXECUTE
        )(self)
