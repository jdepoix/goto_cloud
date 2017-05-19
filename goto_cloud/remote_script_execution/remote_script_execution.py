import base64

import json

from remote_execution.public import RemoteHostExecutor

from remote_host_command.public import RemoteHostCommand


class RemoteScriptExecutor():
    """
    takes care of executing a given python script on a remote host and injecting environment variables
    """
    REMOTE_SCRIPT_BASE_TEMPLATE = (
        'import base64;import json;CONTEXT = json.loads(base64.b64decode({env_string}));{script_string}'
    )
    PYTHON_SCRIPT_EXECUTION_COMMAND = RemoteHostCommand('python -c "{SCRIPT}"')

    def __init__(self, remote_host):
        """
        
        :param remote_host: the remote host to execute on
        :type remote_host: remote_host.public.RemoteHost
        """
        self.remote_executor = RemoteHostExecutor(remote_host)

    def execute(self, script, env=None):
        """
        executes the given script on the remote host and injects the env dict as a CONTEXT dict into the script
        
        :param script: the script to execute
        :type script: str
        :param env: the env to inject into the script
        :type env: dict
        :return: the stdout of the script execution
        :rtype: str
        """
        return self.remote_executor.execute(self._render_script_execution_command(script, env))

    def _render_script_execution_command(self, script, env):
        return self.PYTHON_SCRIPT_EXECUTION_COMMAND.render(
            script=self.REMOTE_SCRIPT_BASE_TEMPLATE.format(
                env_string=self._render_env(env),
                script_string=self._render_script_string(script),
            ).replace('"', '\\"')
        )

    def _render_env(self, env):
        return base64.b64encode(json.dumps(env if env else {}).encode())

    def _render_script_string(self, script):
        return script.replace('\n', ';')
