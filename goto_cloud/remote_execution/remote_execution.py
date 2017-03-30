from abc import ABCMeta, abstractmethod

from paramiko import SSHClient, AutoAddPolicy


class RemoteExecutor(metaclass=ABCMeta):
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
            self.remote_client.close()

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
