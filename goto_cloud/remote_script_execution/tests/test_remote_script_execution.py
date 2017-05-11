from django.test import TestCase

from test_assets.public import TestAsset

from remote_host.public import RemoteHost

from ..remote_script_execution import RemoteScriptExecutor


class TestRemoteScriptExecutor(TestCase, metaclass=TestAsset.PatchTrackedRemoteExecutionMeta):
    def test_execute(self):
        remote_script_executor = RemoteScriptExecutor(RemoteHost.objects.create(address='ubuntu16'))

        env = {
            '1': 1,
            '2': 2,
            '3': 3
        }

        remote_script_executor.execute('script', env)

        self.assertIn(
            # TODO add env stuff
            '(script)',
            self.executed_commands
        )

    def test_execute__no_env(self):
        remote_script_executor = RemoteScriptExecutor(RemoteHost.objects.create(address='ubuntu16'))

        remote_script_executor.execute('script')

        self.assertIn(
            '(script)',
            self.executed_commands
        )