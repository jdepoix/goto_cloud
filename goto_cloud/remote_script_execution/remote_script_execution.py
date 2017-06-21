import base64

from remote_execution.public import RemoteHostExecutor

from remote_host_command.public import RemoteHostCommand


class RemoteScriptExecutor():
    """
    takes care of executing a given python script on a remote host and injecting environment variables
    """
    REMOTE_SCRIPT_BASE_TEMPLATE = (
        'CONTEXT = {env_string}\n{script_string}'
    )
    PYTHON_SCRIPT_EXECUTION_COMMAND = RemoteHostCommand(
        '{SUDO_PREFIX}python -c "import base64;exec(base64.b64decode({ENCODED_SCRIPT}))"'
    )

    def __init__(self, remote_host):
        """
        
        :param remote_host: the remote host to execute on
        :type remote_host: remote_host.public.RemoteHost
        """
        self.remote_executor = RemoteHostExecutor(remote_host)

    def execute(self, script, env=None, sudo=False):
        """
        executes the given script on the remote host and injects the env dict as a CONTEXT dict into the script
        
        :param script: the script to execute
        :type script: str
        :param env: the env to inject into the script
        :type env: dict
        :param sudo: whether the script should be executed as sudo or not
        :type sudo: bool
        :return: the stdout of the script execution
        :rtype: str
        """
        return self.remote_executor.execute(self._render_script_execution_command(script, env, sudo))

    def _render_script_execution_command(self, script, env, sudo):
        return self.PYTHON_SCRIPT_EXECUTION_COMMAND.render(
            sudo_prefix='sudo ' if sudo else '',
            encoded_script=self._encode_script(
                self.REMOTE_SCRIPT_BASE_TEMPLATE.format(
                    env_string=self._render_env(env),
                    script_string=script,
                )
            ),
        )

    def _render_env(self, env):
        return str(env if env else {})

    def _encode_script(self, rendered_script):
        return base64.b64encode(rendered_script.encode())
