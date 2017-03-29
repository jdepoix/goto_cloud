from io import BytesIO

from unittest import TestCase
from unittest.mock import patch

from remote_execution.remote_execution import RemoteExecutor, SshRemoteExecutor


def connect_mock(self, *ags, **kwargs):
    self.connected = True

def close_mock(self, *ags, **kwargs):
    self.connected = False

def execute_mock(self, command):
    test_commands = {
        'successful_command': (BytesIO(b''), BytesIO(b'Command Success'), BytesIO(b'')),
        'error_command': (BytesIO(b''), BytesIO(b''), BytesIO(b'Command Error'))
    }

    return test_commands[command]


@patch('paramiko.SSHClient.connect', connect_mock)
@patch('paramiko.SSHClient.close', close_mock)
@patch('paramiko.SSHClient.get_transport', lambda self: self.connected if self.connected else None)
@patch('paramiko.SSHClient.exec_command', execute_mock)
class TestSshRemoteExecutor(TestCase):
    @patch('paramiko.SSHClient.connect', connect_mock)
    def setUp(self):
        self.remote_executor = SshRemoteExecutor('test')

    def test_close(self):
        self.assertTrue(self.remote_executor.remote_client.connected)
        self.remote_executor.close()
        self.assertFalse(self.remote_executor.remote_client.connected)

    def test_connect(self):
        self.assertTrue(self.remote_executor.remote_client.connected)

    def test_reconnect(self):
        self.assertTrue(self.remote_executor.is_connected())
        self.remote_executor.reconnect()
        self.assertTrue(self.remote_executor.is_connected())

    def test_is_connected(self):
        self.assertTrue(self.remote_executor.is_connected())
        self.remote_executor.close()
        self.assertFalse(self.remote_executor.is_connected())

    def test_execute(self):
        self.assertEqual(self.remote_executor.execute('successful_command'), 'Command Success')

    def test_execute__after_close(self):
        self.remote_executor.close()
        self.remote_executor.execute('successful_command')
        self.assertTrue(self.remote_executor.is_connected())

    def test_execute__fail(self):
        with self.assertRaises(RemoteExecutor.ExecutionException) as context_manager:
            self.remote_executor.execute('error_command')

        self.assertIn('Command Error', str(context_manager.exception))
