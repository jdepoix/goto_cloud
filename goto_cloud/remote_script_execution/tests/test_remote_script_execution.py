import base64

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
            '3': 3,
            '4': '{"test_\'new\'_line": "\n"}'
        }

        remote_script_executor.execute('script', env)

        self.assertIn(
            'python -c "import base64;exec(base64.b64decode({encoded_script}))"'.format(
                encoded_script=base64.b64encode(
                    RemoteScriptExecutor.REMOTE_SCRIPT_BASE_TEMPLATE.format(
                        env_string=str(env),
                        script_string='script'
                    ).encode()
                )
            ),
            self.executed_commands
        )

    def test_execute__no_env(self):
        remote_script_executor = RemoteScriptExecutor(RemoteHost.objects.create(address='ubuntu16'))

        remote_script_executor.execute('script')

        'python -c "import base64;exec(base64.b64decode({encoded_script}))"'.format(
            encoded_script=base64.b64encode(
                RemoteScriptExecutor.REMOTE_SCRIPT_BASE_TEMPLATE.format(
                    env_string=str({}),
                    script_string='script'
                ).encode()
            )
        ),

    def test_execute__sudo(self):
        remote_script_executor = RemoteScriptExecutor(RemoteHost.objects.create(address='ubuntu16'))

        env = {
            '1': 1,
            '2': 2,
            '3': 3,
            '4': '{"test_\'new\'_line": "\n"}'
        }

        remote_script_executor.execute('script', env=env, sudo=True)

        self.assertIn(
            'sudo python -c "import base64;exec(base64.b64decode({encoded_script}))"'.format(
                encoded_script=base64.b64encode(
                    RemoteScriptExecutor.REMOTE_SCRIPT_BASE_TEMPLATE.format(
                        env_string=str(env),
                        script_string='script'
                    ).encode()
                )
            ),
            self.executed_commands
        )
