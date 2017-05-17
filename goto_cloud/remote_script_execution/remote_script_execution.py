import json

from remote_execution.public import RemoteHostExecutor

from remote_host_command.public import RemoteHostCommand


class RemoteScriptExecutor():
    REMOTE_SCRIPT_BASE_TEMPLATE = 'import json\nCONTEXT = json.loads(\'{env_string}\')\n{script_string}'
    PYTHON_SCRIPT_EXECUTION_COMMAND = RemoteHostCommand('printf "{SCRIPT}" | python')

    def __init__(self, remote_host):
        self.remote_executor = RemoteHostExecutor(remote_host)

    def execute(self, script, env=None):
        return self.remote_executor.execute(self._render_script_execution_command(script, env))

    def _render_env(self, env):
        return json.dumps(env if env else {})

    def _render_script_execution_command(self, script, env):
        return self.PYTHON_SCRIPT_EXECUTION_COMMAND.render(
            script=self.REMOTE_SCRIPT_BASE_TEMPLATE.format(
                env_string=self._render_env(env),
                script_string=script
            ).replace('"', '\\"')
        )
