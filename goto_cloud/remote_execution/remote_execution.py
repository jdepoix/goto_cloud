from abc import ABCMeta, abstractmethod

from paramiko import SSHClient, AutoAddPolicy

from operating_system.public import OperatingSystem

from operating_system_support.public import PartiallySupported


class RemoteExecutor(PartiallySupported, metaclass=ABCMeta):
    """
    Takes care of executing commands on a remote host. This class can be subclassed, to execute remote executing, using
    different kinds of remote clients, for different systems.
    """
    class ExecutionException(Exception):
        """
        is raised when an error occurs, during the execution of a command on the remote host 
        """
        pass


    def __init__(self, hostname, username=None, password=None, port=22):
        """
        initializes the RemoteExecutor and opens a connection using the implemented remote client
        
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
        self.connect()

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

    def execute(self, command):
        """
        executes the given command on the remote host and parses the returned output
        
        :param command: the command to execute
        :type command: str
        :return: the output the command produced
        :rtype: str
        :raises RemoteExecutor.ExecutionException: in case something goes wrong during execution 
        """
        if not self.is_connected():
            self.connect()

        _, stdout, stderr = self._execute(command)

        stderr_output = stderr.read()

        if stderr_output:
            raise RemoteExecutor.ExecutionException(
                'While executing:\n{command}\n\nThe following Error occurred:\n{error}'.format(
                    command=command,
                    error=stderr_output.decode(),
                )
            )

        return stdout.read().decode().strip()

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

    @classmethod
    def _get_supported_operating_systems(cls):
        return OperatingSystem.LINUX,

    def connect(self):
        self.remote_client = SSHClient()
        self.remote_client.set_missing_host_key_policy(AutoAddPolicy())
        self.remote_client.connect(self.hostname, username=self.username, password=self.password, port=self.port)

    def _close(self):
        self.remote_client.close()

    def is_connected(self):
        return self.remote_client and self.remote_client.get_transport() is not None

    def _execute(self, command):
        return self.remote_client.exec_command(command)


class RemoteHostExecutor():
    """
    takes care of the remote execution for a given RemoteHost
    """
    class UnsupportedOperatingSystemException(Exception):
        """
        is raised, if the operating system of the given remote host is not supported
        """
        pass

    REMOTE_EXECUTORS = (SshRemoteExecutor,)
    """
    a tuple of all RemoteExecutors which could possibly be used, depending on their OS support
    """

    def __init__(self, remote_host):
        """
        
        :param remote_host: the remote host to execute on
        :type remote_host: remote_host.public.RemoteHost
        """
        self.remote_executor = self._get_remote_executor(remote_host)

    def _get_remote_executor(self, remote_host):
        """
        return a supported RemoteExecutor for the given RemoteHost
        
        :param remote_host: the remote host you want to get a RemoteExecutor for
        :type remote_host: remote_host.public.RemoteHost
        :return: the remote executor
        :rtype: RemoteExecutor
        :raises: operating_system.public.OperatingSystem.NotSupportedException
        """
        for remote_execution_class in self.REMOTE_EXECUTORS:
            if remote_execution_class.is_supported(remote_host.os):
                return remote_execution_class(
                    hostname=remote_host.address,
                    username=remote_host.username if remote_host.username else None,
                    password=remote_host.password if remote_host.password else None,
                    port=remote_host.port if remote_host.port else None,
                )

        raise OperatingSystem.NotSupportedException()


    def close(self):
        return self.remote_executor.close()

    def connect(self):
        return self.remote_executor.connect()

    def reconnect(self):
        return self.remote_executor.reconnect()

    def is_connected(self):
        return self.remote_executor.is_connected()

    def execute(self, command):
        return self.remote_executor.execute(command)
