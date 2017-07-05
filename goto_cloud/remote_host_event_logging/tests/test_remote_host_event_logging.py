from unittest import TestCase

from testfixtures import test_datetime, replace
from testfixtures.logcapture import log_capture

from remote_host.public import RemoteHost

from ..remote_host_event_logging import RemoteHostEventLogger


class TestSourceEventLogging(TestCase):
    def setUp(self):
        self.logger = RemoteHostEventLogger(
            RemoteHost.objects.create(address='test.com')
        )
        self.expected_message = (
            '\n+------------- [2000-01-01 12:00:00] <test.com> -------------\n'
            '| test message\n'
            '+------------------------------------------------------------\n'
        )

    @replace(
        'remote_host_event_logging.remote_host_event_logging.datetime.datetime', test_datetime(2000, 1, 1, 12, 0, 0)
    )
    @log_capture()
    def test_debug(self, log):
        self.logger.debug('test message')
        log.check(
            (
                'goto_cloud.remote_host_event_logging.remote_host_event_logging',
                'DEBUG',
                self.expected_message
            )
        )

    @replace(
        'remote_host_event_logging.remote_host_event_logging.datetime.datetime', test_datetime(2000, 1, 1, 12, 0, 0)
    )
    @log_capture()
    def test_info(self, log):
        self.logger.info('test message')
        log.check(
            (
                'goto_cloud.remote_host_event_logging.remote_host_event_logging',
                'INFO',
                self.expected_message
            )
        )

    @replace(
        'remote_host_event_logging.remote_host_event_logging.datetime.datetime', test_datetime(2000, 1, 1, 12, 0, 0)
    )
    @log_capture()
    def test_warning(self, log):
        self.logger.warning('test message')
        log.check(
            (
                'goto_cloud.remote_host_event_logging.remote_host_event_logging',
                'WARNING',
                self.expected_message
            )
        )

    @replace(
        'remote_host_event_logging.remote_host_event_logging.datetime.datetime', test_datetime(2000, 1, 1, 12, 0, 0)
    )
    @log_capture()
    def test_error(self, log):
        self.logger.error('test message')
        log.check(
            (
                'goto_cloud.remote_host_event_logging.remote_host_event_logging',
                'ERROR',
                self.expected_message
            )
        )

    @replace(
        'remote_host_event_logging.remote_host_event_logging.datetime.datetime', test_datetime(2000, 1, 1, 12, 0, 0)
    )
    @log_capture()
    def test_critical(self, log):
        self.logger.critical('test message')
        log.check(
            (
                'goto_cloud.remote_host_event_logging.remote_host_event_logging',
                'CRITICAL',
                self.expected_message
            )
        )
