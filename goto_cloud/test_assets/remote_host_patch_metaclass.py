from unittest.mock import patch


def mocked_execute(remote_executor, command):
    from .test_assets import TestAsset
    return TestAsset.REMOTE_HOST_MOCKS[remote_executor.hostname].execute(
        command
    )

class PatchRemoteHostMeta(type):
    """
    can be used as a metaclass for a TestCase to patch relevant methods, required to mock a RemoteHost
    """
    MOCKED_EXECUTE = mocked_execute

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patch('remote_execution.remote_execution.SshRemoteExecutor.connect', lambda self: None)(self)
        patch('remote_execution.remote_execution.SshRemoteExecutor.close', lambda self: None)(self)
        patch('remote_execution.remote_execution.SshRemoteExecutor.is_connected', lambda self: True)(self)
        patch(
            'remote_execution.remote_execution.SshRemoteExecutor._execute',
            PatchRemoteHostMeta.MOCKED_EXECUTE
        )(self)
