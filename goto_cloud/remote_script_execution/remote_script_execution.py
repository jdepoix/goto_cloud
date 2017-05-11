from remote_execution.remote_execution import RemoteHostExecutor


class RemoteScriptExecutor():
    def __init__(self, remote_host):
        self.remote_executor = RemoteHostExecutor(remote_host)

    def execute(self, script, env=None):
        return self.remote_executor.execute(self._render_script_execution_command(script, env))

    def _render_env(self, env):
        if env:
            # TODO render env
            return ''
        else:
            return ''

    def _render_script_execution_command(self, script, env):
        return '({env}{script})'.format(
            script=script,
            env=self._render_env(env),
        )
