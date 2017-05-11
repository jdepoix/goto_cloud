from enums.public import StringEnum
from remote_script_execution.remote_script_execution import RemoteScriptExecutor


class HookEventHandler():
    class EventType(StringEnum):
        BEFORE = 'BEFORE'
        AFTER = 'AFTER'

    class ExecutionLocations(StringEnum):
        SOURCE = 'SOURCE'
        TARGET = 'TARGET'

    def __init__(self, hooks):
        self.hooks = hooks

    def emit(self, source, event_type):
        hook_name = '_'.join((source.status, event_type))

        if hook_name in self.hooks:
            self._get_remote_script_executor(
                self.hooks[hook_name],
                source
            ).execute(
                self.hooks[hook_name]['execute'],
                self._load_script_env(source)
            )

    def _get_remote_script_executor(self, hook, source):
        if hook['location'] == self.ExecutionLocations.TARGET:
            return RemoteScriptExecutor(source.target.remote_host)

        return RemoteScriptExecutor(source.remote_host)

    def _load_script_env(self, source):
        # TODO
        return {}
