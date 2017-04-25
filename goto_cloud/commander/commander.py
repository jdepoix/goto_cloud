from abc import ABCMeta, abstractmethod

from command.command import SourceCommand


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

    # TODO error handling and persistent status logging
    def _execute(self):
        current_command_class = self._commander_driver.get(self._source.status)
        signal = None
        if current_command_class:
            current_command = self._initialize_command(current_command_class)
            signal = current_command.execute()
        if (
            self._source.status != self._source.lifecycle[-1]
            and (signal is None or signal is not None and signal != Commander.Signal.SLEEP)
        ):
            self._source.increment_status()
            self.execute()

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
