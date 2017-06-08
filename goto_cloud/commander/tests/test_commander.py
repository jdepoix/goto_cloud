from unittest import TestCase

from command.public import SourceCommand

from enums.public import StringEnum

from source.public import Source

from ..commander import Commander


class TestSource(Source):
    class Meta():
        app_label = 'test'

    class Status(StringEnum):
        FIRST = 'FIRST'
        SECOND = 'SECOND'
        THIRD = 'THIRD'
        FORTH = 'FORTH'
        FIFTH = 'FIFTH'

    def __getattribute__(self, item):
        if item == 'remote_host':
            return None
        return super().__getattribute__(item)

    @property
    def lifecycle(self):
        return (
            TestSource.Status.FIRST,
            TestSource.Status.SECOND,
            TestSource.Status.FORTH,
            TestSource.Status.FIFTH,
        )

    def increment_status(self):
        self.status = self._lifecycle_manager.get_next_status()


class DefaultCommand(SourceCommand):
    def _execute(self):
        pass


class SleepCommand(SourceCommand):
    def _execute(self):
        return Commander.Signal.SLEEP


class DefaultCommander(Commander):
    @property
    def _commander_driver(self):
        return {
            TestSource.Status.FIRST: DefaultCommand,
            TestSource.Status.SECOND: DefaultCommand,
            TestSource.Status.THIRD: DefaultCommand,
            TestSource.Status.FORTH: DefaultCommand,
            TestSource.Status.FIFTH: DefaultCommand,
        }


class SkippingDefaultCommander(Commander):
    @property
    def _commander_driver(self):
        return {
            TestSource.Status.SECOND: DefaultCommand,
            TestSource.Status.FORTH: DefaultCommand,
        }


class SleepCommander(Commander):
    @property
    def _commander_driver(self):
        return {
            TestSource.Status.FIRST: DefaultCommand,
            TestSource.Status.SECOND: DefaultCommand,
            TestSource.Status.THIRD: DefaultCommand,
            TestSource.Status.FORTH: SleepCommand,
            TestSource.Status.FIFTH: DefaultCommand,
        }


class TestCommander(TestCase):
    def setUp(self):
        self.test_source = TestSource()

    def test_execute(self):
        self.assertEquals(self.test_source.status, TestSource.Status.FIRST)
        DefaultCommander(self.test_source).execute()
        self.assertEquals(self.test_source.status, TestSource.Status.FIFTH)

    def test_execute__skip_statuses(self):
        self.assertEquals(self.test_source.status, TestSource.Status.FIRST)
        SkippingDefaultCommander(self.test_source).execute()
        self.assertEquals(self.test_source.status, TestSource.Status.FIFTH)

    def test_execute__sleep(self):
        self.assertEquals(self.test_source.status, TestSource.Status.FIRST)
        SleepCommander(self.test_source).execute()
        self.assertEquals(self.test_source.status, TestSource.Status.FORTH)
        SleepCommander(self.test_source).execute()
        self.assertEquals(self.test_source.status, TestSource.Status.FORTH)

    def test_increment_status_and_execute(self):
        self.assertEquals(self.test_source.status, TestSource.Status.FIRST)
        SleepCommander(self.test_source).execute()
        self.assertEquals(self.test_source.status, TestSource.Status.FORTH)
        SleepCommander(self.test_source).increment_status_and_execute()
