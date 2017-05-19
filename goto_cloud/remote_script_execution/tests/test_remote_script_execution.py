import json

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
            '4': '{"test_new_line": "\n"}'
        }

        remote_script_executor.execute('script', env)

        self.assertIn(
            'python -c "import base64;import json;'
            'CONTEXT = json.loads(base64.b64decode({encoded_env}));'
            'script"'.format(encoded_env=base64.b64encode(json.dumps(env).encode())),
            self.executed_commands
        )

    def test_execute__no_env(self):
        remote_script_executor = RemoteScriptExecutor(RemoteHost.objects.create(address='ubuntu16'))

        remote_script_executor.execute('script')

        self.assertIn(
            'python -c "import base64;import json;'
            'CONTEXT = json.loads(base64.b64decode({encoded_env}));'
            'script"'.format(encoded_env=base64.b64encode(json.dumps({}).encode())),
            self.executed_commands
        )
