from abc import ABCMeta, abstractmethod

from command.public import SourceCommand

from hook_handling.public import HookEventHandler


class Commander(SourceCommand, metaclass=ABCMeta):
    class Signal():
        """
        a signal can be returned by a Commands execute or rollback method, to trigger a certain behaviour of the
        Commander
        """
        SLEEP = 'SLEEP'

    def __init__(self, source):
        """
        The Commander is initialized with a Source instance and the commander driver.

        :param source: the Source in whose context the Command will be executed
        :type source: source.public.Source
        """
        super().__init__(source)
        self.hook_event_handler = HookEventHandler(source)

    def _execute(self):
        current_command_class = self._commander_driver.get(self._source.status)
        signal = None
        if current_command_class:
            signal = self._execute_command(current_command_class)
        if (
            self._source.status != self._source.lifecycle[-1]
            and (signal is None or signal != Commander.Signal.SLEEP)
        ):
            self._source.increment_status()
            self.execute()

    def _execute_command(self, command_class):
        """
        initialized and executes the given command class

        :param command_class: the class of the command you want to execute
        :type command_class: SourceCommand.__class__
        :return: the signal the executed command returned, in case it did return a signal
        """
        # TODO error handling and persistent status logging
        current_command = self._initialize_command(command_class)
        self.logger.debug('start executing {command_name} on {source_hostname}'.format(
            command_name=str(command_class),
            source_hostname=self._source.remote_host.system_info.get('network', {}).get('hostname', 'unknown host')
            if self._source.remote_host else 'unknown host'
        ))
        self.hook_event_handler.emit(HookEventHandler.EventType.BEFORE)
        signal = current_command.execute()
        self.hook_event_handler.emit(HookEventHandler.EventType.AFTER)
        self.logger.debug('finished executing {command_name} on {source_hostname}'.format(
            command_name=str(command_class),
            source_hostname=self._source.remote_host.system_info.get('network', {}).get('hostname', 'unknown host')
            if self._source.remote_host else 'unknown host'
        ))
        return signal

    def increment_status_and_execute(self):
        """
        starts execution beginning with the next status
        
        """
        self._source.increment_status()
        self.execute()

    def _initialize_command(self, command_class):
        """
        This method is used, to initialize a given Command. This can easily be overwritten, to change the way the
        Commands are initialized

        :param command_class: the class for the Command
        :type command_class: SourceCommand.__class__()
        :return: the Command instance
        :rtype: SourceCommand
        """
        return command_class(self._source)

    @property
    @abstractmethod
    def _commander_driver(self):
        """
        returns the mapping of status to command, which is used in this Commander
        
        :return: the command mapping
        :rtype: dict
        """
        pass
