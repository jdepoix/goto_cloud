from abc import ABCMeta, abstractmethod

from source_event_logging.public import SourceEventLogger


class Command(metaclass=ABCMeta):
    """
    Represents a executable unit. The execute method can be overwritten, to implement a plugable, self-contained 
    execution
    """
    @abstractmethod
    def execute(self):
        """
        executes the command

        :return: does not return anything, except for a Commander.Signal, in case a Signal is given to the executing
        unit
        :rtype: None | str
        """
        pass


class SourceCommand(Command, metaclass=ABCMeta):
    """
    A Command which specifically executes in the context of a given Source
    """
    EVENT_LOGGER = SourceEventLogger

    def __init__(self, source):
        """
        :param source: the Source in whose context the Command will be executed
        :type source: source.public.Source
        """
        self._source = source
        self._target = source.target
        self.logger = self.EVENT_LOGGER(source)
