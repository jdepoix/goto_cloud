from io import BytesIO

import unittest
from unittest.mock import patch

from django.test import TestCase

from operating_system.public import OperatingSystem
from remote_host.public import RemoteHost

from ..remote_execution import RemoteExecutor, SshRemoteExecutor, RemoteHostExecutor


def connect_mock(self, *args, **kwargs):
    self.connected = True


def close_mock(self):
    self.connected = False


def execute_mock(self, command):
    test_commands = {
        'successful_command': (BytesIO(b''), BytesIO(b'Command Success'), BytesIO(b'')),
        'error_command': (BytesIO(b''), BytesIO(b''), BytesIO(b'Command Error'))
    }

    return test_commands[command]


@patch('paramiko.SSHClient.close', close_mock)
@patch('paramiko.SSHClient.get_transport', lambda self: self.connected if self.connected else None)
@patch('paramiko.SSHClient.exec_command', execute_mock)
class TestSshRemoteExecutor(unittest.TestCase):
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


@patch('paramiko.SSHClient.connect', connect_mock)
@patch('paramiko.SSHClient.close', close_mock)
@patch('paramiko.SSHClient.get_transport', lambda self: self.connected if self.connected else None)
@patch('paramiko.SSHClient.exec_command', execute_mock)
class TestRemoteHostExecutor(TestCase, TestSshRemoteExecutor):
    @patch('paramiko.SSHClient.connect', connect_mock)
    def setUp(self):
        self.remote_executor = RemoteHostExecutor(RemoteHost.objects.create(os=OperatingSystem.LINUX))

    def test_initialization(self):
        self.assertTrue(
            isinstance(
                RemoteHostExecutor(
                    RemoteHost.objects.create(
                        os=OperatingSystem.LINUX,
                    )
                ).operator,
                SshRemoteExecutor
            )
        )

    def test_initialization__os_related(self):
        self.assertTrue(
            isinstance(
                RemoteHostExecutor(
                    RemoteHost.objects.create(
                        os=OperatingSystem.UBUNTU,
                    )
                ).operator,
                SshRemoteExecutor
            )
        )

    def test_initialization__os_not_supported(self):
        with self.assertRaises(OperatingSystem.NotSupportedException):
            RemoteHostExecutor(RemoteHost.objects.create(os=OperatingSystem.WINDOWS))

    def test_close(self):
        self.assertTrue(self.remote_executor.operator.remote_client.connected)
        self.remote_executor.close()
        self.assertFalse(self.remote_executor.operator.remote_client.connected)

    def test_connect(self):
        self.remote_executor.close()
        self.assertFalse(self.remote_executor.operator.remote_client.connected)
        self.remote_executor.connect()
        self.assertTrue(self.remote_executor.operator.remote_client.connected)
