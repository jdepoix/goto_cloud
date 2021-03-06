import logging

import traceback

from abc import ABCMeta, abstractmethod

from remote_host_event_logging.public import RemoteHostEventLogger


class Command(metaclass=ABCMeta):
    """
    Represents a executable unit. The execute method can be overwritten, to implement a plugable, self-contained 
    execution
    """
    class CommandExecutionException(Exception):
        """
        base exception for exception which occur during command execution and take an error report, to provide a 
        (hopefully) helpful error message
        
        """
        COMMAND_DOES = 'execute something'

        def __init__(self, error_report):
            super().__init__(
                'While trying to {command_does}, the following errors occurred. Please resolves these '
                'manually and then skip this step:\n\n{errors}'.format(
                    errors=error_report,
                    command_does=self.COMMAND_DOES
                )
            )

    ERROR_REPORT_LINE_SEPARATOR = '\n\n-------------------------------------------------------------\n\n'
    ERROR_REPORT_EXCEPTION_CLASS = CommandExecutionException

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute(self):
        """
        executes the command

        :return: does not return anything, except for a Commander.Signal, in case a Signal is given to the executing
        unit
        :rtype: None | str
        """
        self.errors = []

        signal = self._execute()

        error_report = self.get_error_report()
        if error_report: self._handle_error_report(error_report)

        return signal

    @abstractmethod
    def _execute(self):
        """
        private implementation of the command execution

        :return: does not return anything, except for a Commander.Signal, in case a Signal is given to the executing
        unit
        :rtype: None | str
        """
        pass

    def get_error_report(self):
        """
        returns the errors which have been collected during execution
        
        :return: errors separated by lines
        :rtype: str
        """
        return Command.ERROR_REPORT_LINE_SEPARATOR.join(self.errors)

    def _add_error(self, error):
        """
        adds an error to the list of collected errors
        
        :param error: errors message to save
        :type error: str
        """
        self.errors.append(error)

    def _handle_error_report(self, error_report):
        """
        This method is called after execution, if there are errors in the error report. This can be overwritten, to
        define a custom way, a extending Command, handles errors
        
        :param error_report: the error report
        :type error_report: str
        """
        raise self.ERROR_REPORT_EXCEPTION_CLASS(error_report)

    @staticmethod
    def _collect_errors(method):
        """
        decorator function, which catches errors raised during the execution of the decorated method and collects them,
        instead of stopping execution
        
        :param method: (self: Command, *args, **kwargs) -> Any
        :return: the decorated method
        :rtype: (self: Command, *args, **kwargs) -> Any
        """
        def wrapped_method(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except Exception as e:
                self.logger.error(traceback.format_exc())
                self._add_error(str(e))

        return wrapped_method


class SourceCommand(Command, metaclass=ABCMeta):
    """
    A Command which specifically executes in the context of a given Source
    """
    EVENT_LOGGER = RemoteHostEventLogger

    def __init__(self, source):
        """
        :param source: the Source in whose context the Command will be executed
        :type source: source.public.Source
        """
        super().__init__()
        self._source = source
        self._target = source.target
        self.logger = self.EVENT_LOGGER(source.remote_host)
