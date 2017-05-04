from remote_host_command.public import RemoteHostCommand


class DefaultRemoteHostCommand():
    """
    a set of default remote host commands
    """
    RELOAD_MOUNTS = RemoteHostCommand('sudo mount -a')
    BIND_MOUNT = RemoteHostCommand('sudo mount -o bind {DIRECTORY} {MOUNTPOINT}')
    MAKE_DIRECTORY = RemoteHostCommand('sudo mkdir {DIRECTORY}')
    CHECK_MOUNTPOINT = RemoteHostCommand('sudo mountpoint {DIRECTORY}')
