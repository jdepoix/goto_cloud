from unittest import TestCase

from testfixtures import test_datetime, replace
from testfixtures.logcapture import log_capture

from source.public import Source

from remote_host.public import RemoteHost

from ..source_event_logging import SourceEventLogger


class TestSourceEventLogging(TestCase):
    def setUp(self):
        self.logger = SourceEventLogger(
            Source.objects.create(remote_host=RemoteHost.objects.create(address='test.com'))
        )
        self.expected_message = '[2000-01-01 12:00:00] <test.com>: test message'

    @replace('source_event_logging.source_event_logging.datetime.datetime', test_datetime(2000, 1, 1, 12, 0, 0))
    @log_capture()
    def test_debug(self, log):
        self.logger.debug('test message')
        log.check(
            (
                'goto_cloud.source_event_logging.source_event_logging',
                'DEBUG',
                self.expected_message
            )
        )

    @replace('source_event_logging.source_event_logging.datetime.datetime', test_datetime(2000, 1, 1, 12, 0, 0))
    @log_capture()
    def test_info(self, log):
        self.logger.info('test message')
        log.check(
            (
                'goto_cloud.source_event_logging.source_event_logging',
                'INFO',
                self.expected_message
            )
        )

    @replace('source_event_logging.source_event_logging.datetime.datetime', test_datetime(2000, 1, 1, 12, 0, 0))
    @log_capture()
    def test_warning(self, log):
        self.logger.warning('test message')
        log.check(
            (
                'goto_cloud.source_event_logging.source_event_logging',
                'WARNING',
                self.expected_message
            )
        )

    @replace('source_event_logging.source_event_logging.datetime.datetime', test_datetime(2000, 1, 1, 12, 0, 0))
    @log_capture()
    def test_error(self, log):
        self.logger.error('test message')
        log.check(
            (
                'goto_cloud.source_event_logging.source_event_logging',
                'ERROR',
                self.expected_message
            )
        )

    @replace('source_event_logging.source_event_logging.datetime.datetime', test_datetime(2000, 1, 1, 12, 0, 0))
    @log_capture()
    def test_critical(self, log):
        self.logger.critical('test message')
        log.check(
            (
                'goto_cloud.source_event_logging.source_event_logging',
                'CRITICAL',
                self.expected_message
            )
        )
