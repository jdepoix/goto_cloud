from remote_host.public import RemoteHost

from test_assets.public import TestAsset

from ..remote_file_edit import RemoteFileEditor

from .utils import MigrationCommanderTestCase


class TestRemoteFileEditor(MigrationCommanderTestCase):
    TEST_FILE_CONTENT = 'this is\na test file\n with some REPLACEME random stuff\nin it'

    def setUp(self):
        super().setUp()
        self.remote_host = RemoteHost.objects.create(address='ubuntu16')
        TestAsset.REMOTE_HOST_MOCKS['ubuntu16'].add_command(
            'sudo cat /etc/testfile.txt',
            self.TEST_FILE_CONTENT
        )

    def test_edit__original_content_retrieved(self):
        RemoteFileEditor(self.remote_host).edit('/etc/testfile.txt', 'REPLACEME', 'REPLACED')

        self.assertIn('sudo cat /etc/testfile.txt', self.executed_commands)

    def test_edit__original_content_replaced(self):
        RemoteFileEditor(self.remote_host).edit('/etc/testfile.txt', 'REPLACEME', 'REPLACED')

        self.assertIn(
            'sudo bash -c "echo -e \\"{new_file_content}\\" > /etc/testfile.txt"'.format(
                new_file_content=self.TEST_FILE_CONTENT.replace('REPLACEME', 'REPLACED')
            ),
            self.executed_commands
        )

    def test_append(self):
        RemoteFileEditor(self.remote_host).append('/etc/testfile.txt', 'append this')

        self.assertIn(
            'sudo bash -c "echo -e \\"append this\\" >> /etc/testfile.txt"',
            self.executed_commands
        )

    def test_write(self):
        RemoteFileEditor(self.remote_host).write('/etc/testfile.txt', 'write this')

        self.assertIn(
            'sudo bash -c "echo -e \\"write this\\" > /etc/testfile.txt"',
            self.executed_commands
        )
