import datetime
import logging


class RemoteHostEventLogger():
    """
    Logs event based on a given RemoteHost. Supports all log levels of the default Logger.
    """
    class DisableLoggingContextManager():
        """
        context manager which disables logging in the managed context
        """
        def __enter__(self):
            logging.disable(logging.CRITICAL)

        def __exit__(self, exc_type, exc_val, exc_tb):
            logging.disable(logging.NOTSET)

    def __init__(self, remote_host):
        """
        initialized with the remote host which the events are logged for
        
        :param remote_host: the remote host to log for
        :type remote_host: remote_host.public.RemoteHost
        """
        self.logger = logging.getLogger(__name__)
        self.remote_host = remote_host

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._format_message(msg), *args, **kwargs)
        print(msg)

    def info(self, msg, *args, **kwargs):
        self.logger.info(self._format_message(msg), *args, **kwargs)
        print(msg)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._format_message(msg), *args, **kwargs)
        print(msg)

    def error(self, msg, *args, **kwargs):
        self.logger.error(self._format_message(msg), *args, **kwargs)
        print(msg)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(self._format_message(msg), *args, **kwargs)
        print(msg)

    @property
    def _logging_message_prefix(self):
        return '[{timestamp}] <{source_address}>'.format(
            source_address=self.remote_host.address if self.remote_host else 'unknown host',
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    def _format_message(self, message):
        formatted_message = '+------------- {message_prefix} -------------'.format(
            message_prefix=self._logging_message_prefix
        )
        if message:
            for line in message.split('\n'):
                formatted_message += '\n| {logging_line}'.format(logging_line=line)
        formatted_message += '\n+--------------{sized_gap}--------------\n'.format(
            sized_gap='-' * len(self._logging_message_prefix)
        )
        return formatted_message
