from io import BytesIO

import unittest
from unittest.mock import patch

from django.test import TestCase

from paramiko.client import SSHClient
from paramiko.ssh_exception import NoValidConnectionsError, AuthenticationException, SSHException

from operating_system.public import OperatingSystem
from remote_host.public import RemoteHost

from ..remote_execution import RemoteExecutor, SshRemoteExecutor, RemoteHostExecutor


class ChannelMock():
    def __init__(self, failing):
        self.failing = failing

    def recv_exit_status(self):
        return 1 if self.failing else 0


class ChannelFileMock():
    def __init__(self, content, failing=False):
        self.file_object = BytesIO(content.encode())
        self.channel = ChannelMock(failing)

    def __getattribute__(self, item):
        if item == 'file_object' or item == 'channel':
            return super().__getattribute__(item)
        return getattr(self.file_object, item)


def connect_mock(self, *args, **kwargs):
    self.connected = True


def close_mock(self):
    self.connected = False


def execute_mock(self, command):
    test_commands = {
        'successful_command': (ChannelFileMock(''), ChannelFileMock('Command Success'), ChannelFileMock('')),
        'error_command': (ChannelFileMock('', True), ChannelFileMock('', True), ChannelFileMock('Command Error', True))
    }

    return test_commands[command]


def raise_exception_mock(exception):
    def raise_exception(self, *args, **kwargs):
        connect_mock(self, *args, **kwargs)
        raise exception

    return raise_exception


@patch('paramiko.SSHClient.connect', connect_mock)
@patch('paramiko.SSHClient.close', close_mock)
@patch('paramiko.SSHClient.get_transport', lambda self: self.connected if self.connected else None)
@patch('paramiko.SSHClient.exec_command', execute_mock)
class TestSshRemoteExecutor(unittest.TestCase):
    def setUp(self):
        self.remote_executor = SshRemoteExecutor('test')

    def test_close(self):
        self.remote_executor.execute('successful_command')
        self.assertTrue(self.remote_executor.remote_client.connected)
        self.remote_executor.close()
        self.assertFalse(self.remote_executor.remote_client.connected)

    def test_connect(self):
        self.remote_executor.execute('successful_command')
        self.assertTrue(self.remote_executor.remote_client.connected)

    def test_reconnect(self):
        self.remote_executor.execute('successful_command')
        self.assertTrue(self.remote_executor.is_connected())
        self.remote_executor.reconnect()
        self.assertTrue(self.remote_executor.is_connected())

    def test_is_connected(self):
        self.remote_executor.execute('successful_command')
        self.assertTrue(self.remote_executor.is_connected())
        self.remote_executor.close()
        self.assertFalse(self.remote_executor.is_connected())

    def test_execute(self):
        self.assertEqual(self.remote_executor.execute('successful_command'), 'Command Success')

    def test_execute__after_close(self):
        self.remote_executor.close()
        self.remote_executor.execute('successful_command')
        self.assertTrue(self.remote_executor.is_connected())

    def test_execute__execution_fail(self):
        with self.assertRaises(RemoteExecutor.ExecutionException) as context_manager:
            self.remote_executor.execute('error_command')

        self.assertIn('Command Error', str(context_manager.exception))

    def test_connect__connection_exception(self):
        SSHClient.connect = raise_exception_mock(SSHException())

        with self.assertRaises(RemoteExecutor.ConnectionException):
            SshRemoteExecutor('test').execute('successful_command')

    def test_connect__authentication_exception(self):
        SSHClient.connect = raise_exception_mock(AuthenticationException())

        with self.assertRaises(RemoteExecutor.AuthenticationException):
            SshRemoteExecutor('test').execute('successful_command')

    def test_connect__no_valid_connection_exception(self):
        SSHClient.connect = raise_exception_mock(NoValidConnectionsError({'127.0.0.1': 22}))

        with self.assertRaises(RemoteExecutor.NoValidConnectionException):
            SshRemoteExecutor('test').execute('successful_command')

    def test_execute__raise_no_exception_on_failure(self):
        self.assertEqual(
            self.remote_executor.execute('error_command', raise_exception_on_failure=False),
            'Command Error'
        )


@patch('paramiko.SSHClient.connect', connect_mock)
@patch('paramiko.SSHClient.connect', connect_mock)
@patch('paramiko.SSHClient.close', close_mock)
@patch('paramiko.SSHClient.get_transport', lambda self: self.connected if self.connected else None)
@patch('paramiko.SSHClient.exec_command', execute_mock)
class TestRemoteHostExecutor(TestCase, TestSshRemoteExecutor):
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
        self.remote_executor.execute('successful_command')
        self.assertTrue(self.remote_executor.operator.remote_client.connected)
        self.remote_executor.close()
        self.assertFalse(self.remote_executor.operator.remote_client.connected)

    def test_connect(self):
        self.remote_executor.execute('successful_command')
        self.remote_executor.close()
        self.assertFalse(self.remote_executor.operator.remote_client.connected)
        self.remote_executor.connect()
        self.assertTrue(self.remote_executor.operator.remote_client.connected)
