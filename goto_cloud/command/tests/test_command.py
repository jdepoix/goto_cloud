from unittest import TestCase

from source_event_logging.public import SourceEventLogger

from ..command import Command


class ErrorCommand(Command):
    def _execute(self):
        self._failing_method()

    @Command._collect_errors
    def _failing_method(self):
        raise Exception('FAILED')


class NoErrorCommand(Command):
    def _execute(self):
        pass

    @Command._collect_errors
    def not_failing_method(self):
        return 'NOT_FAILED'


class TestCommand(TestCase):
    def test_collect_errors(self):
        command = ErrorCommand()
        try:
            with SourceEventLogger.DisableLoggingContextManager():
                command.execute()
        except:
            pass

        self.assertEqual(command.get_error_report(), 'FAILED')

    def test_collect_errors__throws_command_execution_exception(self):
        command = ErrorCommand()

        with SourceEventLogger.DisableLoggingContextManager():
            with self.assertRaises(Command.CommandExecutionException):
                command.execute()

    def test_collect_errors__not_failed(self):
        command = NoErrorCommand()
        command.execute()
        self.assertEqual(command.not_failing_method(), 'NOT_FAILED')
        self.assertEqual(command.get_error_report(), '')
