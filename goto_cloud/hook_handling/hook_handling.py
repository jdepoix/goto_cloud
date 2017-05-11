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

    def __init__(self, hooks):
        """
        is initialized with a dict of hooks
        
        :param hooks: mapping of events onto the hooks which should be triggered, when the event is emitted
        :type hooks: dict
        """
        self.hooks = hooks

    def emit(self, source, event_type):
        """
        Emits a event and therefore the listening hooks, if there are any. Which event is emitted eventually, is 
        determined by the event type plus the status the given source is currently in.
        
        :param source: source the event is about
        :type source: source.public.Source
        :param event_type: specifies the type of event
        :type event_type: str
        """
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
        """
        returns the remote script executor which will be used to execute a hook
        
        :param hook: the hook to execute
        :type hook: dict
        :param source: the source to execute the hook for
        :type source: source.public.Source
        :return: 
        """
        if hook['location'] == self.ExecutionLocations.TARGET:
            return RemoteScriptExecutor(source.target.remote_host)

        return RemoteScriptExecutor(source.remote_host)

    def _load_script_env(self, source):
        """
        loads the environment variables which will be injected into the script execution
        
        :param source: the source to load the environment variables for
        :type source: source.public.Source
        :return: the loaded env
        :rtype: dict
        """
        # TODO
        return {}
