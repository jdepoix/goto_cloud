import datetime
import logging


class SourceEventLogger():
    """
    Logs event based on given Source. Supports all log levels of the default Logger. 
    """
    class DisableLoggingContextManager():
        """
        context manager which disables logging in the managed context
        """
        def __enter__(self):
            logging.disable(logging.CRITICAL)

        def __exit__(self, exc_type, exc_val, exc_tb):
            logging.disable(logging.NOTSET)

    def __init__(self, source):
        """
        initialized with the source which the events are logged for
        
        :param source: the source to log for
        :type source: source.public.Source
        """
        self.logger = logging.getLogger(__name__)
        self.source = source

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self._format_message(msg), *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(self._format_message(msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._format_message(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(self._format_message(msg), *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(self._format_message(msg), *args, **kwargs)

    @property
    def _logging_message_prefix(self):
        return '[{timestamp}] <{source_address}>: '.format(
            source_address=self.source.remote_host.address if self.source.remote_host else 'unknown host',
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    def _format_message(self, msg):
        return self._logging_message_prefix + msg
