import time

from abc import ABCMeta, abstractmethod

from paramiko import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError, AuthenticationException

from operating_system.public import OperatingSystem

from operating_system_support.public import AbstractedRemoteHostOperator


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

    def __init__(self, hostname, username=None, password=None, port=22):
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
        """
        self.remote_client = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port

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
    def execute(self, command, raise_exception_on_failure=True):
        """
        executes the given command on the remote host and parses the returned output
        
        :param command: the command to execute
        :type command: str
        :param raise_exception_on_failure: if this is true and the command will return an exit code different than 0,
        an exception will be thrown, if false execution won't be interrupted and stderr is returned
        :type raise_exception_on_failure: bool
        :return: the output the command produced
        :rtype: str
        :raises RemoteExecutor.ExecutionException: in case something goes wrong during execution 
        """
        if not self.is_connected():
            self.connect()

        execution_result = self._execute(command)

        if execution_result['exit_code'] != 0:
            if raise_exception_on_failure:
                raise RemoteExecutor.ExecutionException(
                    'While executing:\n{command}\n\nThe following Error occurred:\n{error}'.format(
                        command=command,
                        error=execution_result['stderr'],
                    )
                )
            else:
                return execution_result['stderr']

        return execution_result['stdout']

    @abstractmethod
    def _execute(self, command):
        """
        does the execution and returns the raw output
        
        :param command: the command to execute
        :type command: str
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
    def _execute(self, command):
        _, stdout, stderr = self.remote_client.exec_command(command)

        stdout_output = stdout.read().decode().strip()
        stderr_output = stderr.read().decode().strip()

        return {
            'exit_code': stdout.channel.recv_exit_status(),
            'stdout': stdout_output,
            'stderr': stderr_output,
        }

    def connect(self):
        try:
            self.remote_client = SSHClient()
            self.remote_client.set_missing_host_key_policy(AutoAddPolicy())
            self.remote_client.connect(self.hostname, username=self.username, password=self.password, port=self.port)
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
        )

    def _execute(self, command): # pragma: no cover
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
