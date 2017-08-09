import time

import logging

from abc import ABCMeta, abstractmethod

from paramiko import SSHClient, AutoAddPolicy
from paramiko.pkey import PKey
from paramiko.ssh_exception import NoValidConnectionsError, AuthenticationException

from operating_system.public import OperatingSystem

from operating_system_support.public import AbstractedRemoteHostOperator

from remote_host_event_logging.public import RemoteHostEventLogger


def catch_and_retry_for(exception_type_to_retry_for, timeout=20, max_tries=15):
    def decorator(function):
        def decorated_function(*args, **kwargs):
            tries = 0
            while True:
                try:
                    return function(*args, **kwargs)
                except exception_type_to_retry_for as exception:
                    if tries >= max_tries:
                        raise exception
                    tries += 1
                    time.sleep(timeout)
        return decorated_function
    return decorator


class RemoteExecutor(metaclass=ABCMeta):
    """
    Takes care of executing commands on a remote host. This class can be subclassed, to execute remote executing, using
    different kinds of remote clients, for different systems.
    """
    class ConnectionException(Exception):
        """
        raised for all kinds of connection errors
        """
        pass

    class AuthenticationException(ConnectionException):
        """
        raised if it's not possible to authenticate
        """
        pass

    class NoValidConnectionException(ConnectionException):
        """
        raised if no valid connection can be established
        """
        pass

    class ExecutionException(Exception):
        """
        is raised when an error occurs, during the execution of a command on the remote host 
        """
        pass

    def __init__(self, hostname, username=None, password=None, port=22, private_key=None, private_key_file_path=None):
        """
        initializes the RemoteExecutor using the implemented remote client
        
        :param hostname: the hostname to use
        :type hostname: str
        :param username: the username to use
        :type username: str
        :param password: the password to use
        :type password: str
        :param port: the port, the remote client should use
        :type port: int
        :private_key: the private ssh key
        :type: private_key: str
        :private_key_file_path: the private ssh key file path
        :type: private_key_file_path: str
        """
        self.remote_client = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.private_key = private_key
        self.private_key_file_path = private_key_file_path
        self.port = port
        self._logger = logging.getLogger(__name__)

    def close(self):
        """
        closes the connection to the remote client, if it is open
        
        """
        if self.is_connected():
            self._close()

    @abstractmethod
    def _close(self):
        """
        closes the connection to the remote client
        
        """
        pass

    @abstractmethod
    def connect(self):
        """
        establish a connection to the remote client
        
        """
        pass

    def reconnect(self):
        """
        closes and reopens the connection to the remote host
        
        """
        self.close()
        self.connect()

    @abstractmethod
    def is_connected(self):
        """
        checks if the connection to the remote host is still open
        
        :return: True if it is still open, False if not
        :rtype: bool
        """
        pass

    @catch_and_retry_for(ConnectionException)
    def execute(self, command, raise_exception_on_failure=True, block_for_response=True):
        """
        executes the given command on the remote host and parses the returned output
        
        :param command: the command to execute
        :type command: str
        :param raise_exception_on_failure: if this is true and the command will return an exit code different than 0,
        an exception will be thrown, if false execution won't be interrupted and stderr is returned
        :type raise_exception_on_failure: bool
        :param block_for_response: if this is true, the method will block until execution is done and return the
        response streams
        :type block_for_response: bool
        :return: the output the command produced
        :rtype: str
        :raises RemoteExecutor.ExecutionException: in case something goes wrong during execution 
        """
        if not self.is_connected():
            self.connect()

        execution_result = self._execute(command, block_for_response)

        if block_for_response:
            if execution_result['exit_code'] != 0:
                error_message = 'While executing:\n{command}\n\nThe following Error occurred:\n{error}'.format(
                    command=command,
                    error=execution_result['stderr'],
                )
                if raise_exception_on_failure:
                    self._logger.critical(error_message)
                    raise RemoteExecutor.ExecutionException(error_message)
                else:
                    self._logger.debug(error_message)
                    return execution_result['stderr']

            self._logger.debug('executed the following command:\n{command}{stdout}{stderr}'.format(
                command=command,
                stdout='\n\nSTDOUT:\n{stdout}'.format(
                    stdout=execution_result['stdout']
                ) if execution_result['stdout'].split() else '',
                stderr='\n\nSTDERR:\n{stderr}'.format(
                    stderr=execution_result['stderr']
                ) if execution_result['stderr'].split() else '',
            ))
            return execution_result['stdout']
        return None

    @abstractmethod
    def _execute(self, command, block_for_response=True):
        """
        does the execution and returns the raw output
        
        :param command: the command to execute
        :type command: str
        :param block_for_response: if this is true, the method will block until execution is done and return the
        response streams
        :type block_for_response: bool
        :return: the return value of the execution
        :rtype: Any
        """
        pass

    def __del__(self):
        self.close()


class SshRemoteExecutor(RemoteExecutor):
    """
    implements RemoteExecutor using SSH as the remote execution client
    """
    def _execute(self, command, block_for_response=True):
        _, stdout, stderr = self.remote_client.exec_command(command)

        if block_for_response:
            stdout_output = stdout.read().decode().strip()
            stderr_output = stderr.read().decode().strip()

            return {
                'exit_code': stdout.channel.recv_exit_status(),
                'stdout': stdout_output,
                'stderr': stderr_output,
            }
        return None

    def connect(self):
        try:
            self.remote_client = SSHClient()
            self.remote_client.set_missing_host_key_policy(AutoAddPolicy())
            self.remote_client.connect(
                self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
                pkey=PKey(self.private_key) if self.private_key else None,
                key_filename=self.private_key_file_path,
            )
        except AuthenticationException as e:
            raise RemoteExecutor.AuthenticationException(str(e))
        except NoValidConnectionsError as e:
            raise RemoteExecutor.NoValidConnectionException(str(e))
        except Exception as e:
            raise RemoteExecutor.ConnectionException(str(e))

    def _close(self):
        self.remote_client.close()

    def is_connected(self):
        return self.remote_client and self.remote_client.get_transport() is not None


class RemoteHostExecutor(AbstractedRemoteHostOperator, RemoteExecutor):
    """
    takes care of the remote execution for a given RemoteHost
    """

    def __init__(self, remote_host):
        super().__init__(remote_host)
        self.operator._logger = RemoteHostEventLogger(remote_host)

    def _get_operating_systems_to_supported_operation_mapping(self):
        return {
            (OperatingSystem.LINUX,): SshRemoteExecutor
        }

    def _init_operator_class(self, operator_class):
        return operator_class(
            hostname=self.remote_host.address,
            username=self.remote_host.username if self.remote_host.username else None,
            password=self.remote_host.password if self.remote_host.password else None,
            port=self.remote_host.port if self.remote_host.port else None,
            private_key=self.remote_host.private_key if self.remote_host.private_key else None,
            private_key_file_path=self.remote_host.private_key_file_path
                if self.remote_host.private_key_file_path else None,
        )

    def _execute(self, command, block_for_response=True): # pragma: no cover
        # At runtime the method of the chosen operator is used. This stub is only to implement the abstract method.
        pass

    def connect(self): # pragma: no cover
        # At runtime the method of the chosen operator is used. This stub is only to implement the abstract method.
        pass

    def is_connected(self): # pragma: no cover
        # At runtime the method of the chosen operator is used. This stub is only to implement the abstract method.
        pass

    def _close(self): # pragma: no cover
        # At runtime the method of the chosen operator is used. This stub is only to implement the abstract method.
        pass

    def __del__(self): # pragma: no cover
        # to make sure the close() method is not triggered twice
        pass
