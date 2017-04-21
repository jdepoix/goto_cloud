from unittest.mock import patch

from test_assets.public import TestAsset


class PatchTrackedRemoteExecution(TestAsset.PatchRemoteHostMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executed_commands = set()
        def tracked_mocked_execute(remote_host, command):
            self.executed_commands.add(command)
            return TestAsset.PatchRemoteHostMeta.MOCKED_EXECUTE(remote_host, command)

        patch(
            'remote_execution.remote_execution.SshRemoteExecutor._execute',
            tracked_mocked_execute
        )(self)
