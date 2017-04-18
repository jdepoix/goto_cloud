from unittest.mock import patch

from .remote_host_mocks import UBUNTU_12_04, UBUNTU_14_04, UBUNTU_16_04


class PatchRemoteHostMeta(type):
    """
    can be used as a metaclass for a TestCase to patch relevant methods, required to mock a RemoteHost
    """
    MOCKS = {
        'ubuntu12': UBUNTU_12_04,
        'ubuntu14': UBUNTU_14_04,
        'ubuntu16': UBUNTU_16_04,
    }

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patch('remote_execution.remote_execution.SshRemoteExecutor.connect', lambda self: None)(cls)
        patch('remote_execution.remote_execution.SshRemoteExecutor.close', lambda self: None)(cls)
        patch('remote_execution.remote_execution.SshRemoteExecutor.is_connected', lambda self: True)(cls)
        patch(
            'remote_execution.remote_execution.SshRemoteExecutor._execute',
            lambda remote_executor, command: PatchRemoteHostMeta.MOCKS[remote_executor.hostname].execute(command)
        )(cls)
