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
    def execute(self):
        pass


class SleepCommand(SourceCommand):
    def execute(self):
        return Commander.Signal.SLEEP


DEFAULT_COMMANDER_DRIVER = {
    TestSource.Status.FIRST: DefaultCommand,
    TestSource.Status.SECOND: DefaultCommand,
    TestSource.Status.THIRD: DefaultCommand,
    TestSource.Status.FORTH: DefaultCommand,
    TestSource.Status.FIFTH: DefaultCommand,
}

SKIPPING_DEFAULT_COMMANDER_DRIVER = {
    TestSource.Status.SECOND: DefaultCommand,
    TestSource.Status.FORTH: DefaultCommand,
}

SLEEP_COMMANDER_DRIVER = {
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
        Commander(self.test_source, DEFAULT_COMMANDER_DRIVER).execute()
        self.assertEquals(self.test_source.status, TestSource.Status.FIFTH)

    def test_execute__skip_statuses(self):
        self.assertEquals(self.test_source.status, TestSource.Status.FIRST)
        Commander(self.test_source, SKIPPING_DEFAULT_COMMANDER_DRIVER).execute()
        self.assertEquals(self.test_source.status, TestSource.Status.FIFTH)

    def test_execute__sleep(self):
        self.assertEquals(self.test_source.status, TestSource.Status.FIRST)
        Commander(self.test_source, SLEEP_COMMANDER_DRIVER).execute()
        self.assertEquals(self.test_source.status, TestSource.Status.FORTH)
        Commander(self.test_source, SLEEP_COMMANDER_DRIVER).execute()
        self.assertEquals(self.test_source.status, TestSource.Status.FORTH)

    def test_increment_status_and_execute(self):
        self.assertEquals(self.test_source.status, TestSource.Status.FIRST)
        Commander(self.test_source, SLEEP_COMMANDER_DRIVER).execute()
        self.assertEquals(self.test_source.status, TestSource.Status.FORTH)
        Commander(self.test_source, SLEEP_COMMANDER_DRIVER).increment_status_and_execute()
