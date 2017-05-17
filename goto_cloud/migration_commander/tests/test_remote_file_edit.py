from remote_execution.public import RemoteHostExecutor

from remote_host.public import RemoteHost

from test_assets.public import TestAsset

from ..remote_file_edit import RemoteFileEditor

from .utils import MigrationCommanderTestCase


class TestRemoteFileEditor(MigrationCommanderTestCase):
    TEST_FILE_CONTENT = 'this is\na test file\n with some REPLACEME random stuff\nin it'

    def _init_test_data(self, **kwargs):
        self.remote_executor = RemoteHostExecutor(RemoteHost.objects.create(address='ubuntu16'))
        TestAsset.REMOTE_HOST_MOCKS['ubuntu16'].add_command(
            'sudo cat /etc/testfile.txt',
            self.TEST_FILE_CONTENT
        )

    def test_edit__original_content_retrieved(self):
        self._init_test_data()

        RemoteFileEditor(self.remote_executor).edit('/etc/testfile.txt', 'REPLACEME', 'REPLACED')

        self.assertIn('sudo cat /etc/testfile.txt', self.executed_commands)

    def test_edit__original_content_replaced(self):
        self._init_test_data()

        RemoteFileEditor(self.remote_executor).edit('/etc/testfile.txt', 'REPLACEME', 'REPLACED')

        self.assertIn(
            'sudo bash -c "echo -e \\"{new_file_content}\\" > /etc/testfile.txt"'.format(
                new_file_content=self.TEST_FILE_CONTENT.replace('REPLACEME', 'REPLACED')
            ),
            self.executed_commands
        )

    def test_edit__no_write_if_replacement_is_not_contained(self):
        self._init_test_data()

        RemoteFileEditor(self.remote_executor).edit('/etc/testfile.txt', 'I_AM_NOT_CONTAINED', 'REPLACED')

        self.assertNotIn(
            'sudo bash -c "echo -e \\"{new_file_content}\\" > /etc/testfile.txt"'.format(
                new_file_content=self.TEST_FILE_CONTENT
            ),
            self.executed_commands
        )

    def test_append(self):
        self._init_test_data()

        RemoteFileEditor(self.remote_executor).append('/etc/testfile.txt', 'append this')

        self.assertIn(
            'sudo bash -c "echo -e \\"append this\\" >> /etc/testfile.txt"',
            self.executed_commands
        )

    def test_append__text_contains_quotation_marks(self):
        self._init_test_data()

        RemoteFileEditor(self.remote_executor).append('/etc/testfile.txt', 'append "this"')

        self.assertIn(
            'sudo bash -c "echo -e \\"append \\"this\\"\\" >> /etc/testfile.txt"',
            self.executed_commands
        )

    def test_write(self):
        self._init_test_data()

        RemoteFileEditor(self.remote_executor).write('/etc/testfile.txt', 'write this')

        self.assertIn(
            'sudo bash -c "echo -e \\"write this\\" > /etc/testfile.txt"',
            self.executed_commands
        )

    def test_write__text_contains_quotation_marks(self):
        self._init_test_data()

        RemoteFileEditor(self.remote_executor).write('/etc/testfile.txt', 'write "this"')

        self.assertIn(
            'sudo bash -c "echo -e \\"write \\"this\\"\\" > /etc/testfile.txt"',
            self.executed_commands
        )
