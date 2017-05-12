from enums.public import StringEnum

from remote_script_execution.public import RemoteScriptExecutor


class HookEventHandler():
    """
    Takes care of letting another instance trigger a hook by emitting a specific event. Which event is emitted 
    eventually, is determined by the event type plus the status the given source is currently in. If a hook is specified
    in the provided hooks, the hook script will be executed on the location, described in the hook, by a 
    RemoteScriptExecutor.
    """
    class EventType(StringEnum):
        """
        Enum to describe a type of event
        """
        BEFORE = 'BEFORE'
        AFTER = 'AFTER'

    class ExecutionLocations(StringEnum):
        """
        Enum to describe where a hook script should be executed
        """
        SOURCE = 'SOURCE'
        TARGET = 'TARGET'

    def __init__(self, source):
        """
        is initialized with a dict of hooks
        
        :param hooks: mapping of events onto the hooks which should be triggered, when the event is emitted
        :type hooks: dict
        """
        self._source = source
        self._cached_hooks = {}

    @property
    def _hooks(self):
        """
        a dict mapping a event to the hook which should be triggered
        
        :return: event to hook mapping
        :rtype: dict
        """
        if not self._cached_hooks and self._source.target:
            self._cached_hooks = self._source.target.blueprint.get('hooks', {})

        return self._cached_hooks

    def emit(self, event_type):
        """
        Emits a event and therefore the listening hooks, if there are any. Which event is emitted eventually, is 
        determined by the event type plus the status the given source is currently in.
        
        :param event_type: specifies the type of event
        :type event_type: str
        """
        hook_name = '_'.join((self._source.status, event_type))

        if hook_name in self._hooks:
            self._get_remote_script_executor(
                self._hooks[hook_name],
            ).execute(
                self._hooks[hook_name]['execute'],
                self._load_script_env()
            )

    def _get_remote_script_executor(self, hook):
        """
        returns the remote script executor which will be used to execute a hook
        
        :param hook: the hook to execute
        :type hook: dict
        :return: 
        """
        if hook['location'] == self.ExecutionLocations.TARGET:
            return RemoteScriptExecutor(self._source.target.remote_host)

        return RemoteScriptExecutor(self._source.remote_host)

    def _load_script_env(self):
        """
        loads the environment variables which will be injected into the script execution
        
        :return: the loaded env
        :rtype: dict
        """
        # TODO
        return {}
