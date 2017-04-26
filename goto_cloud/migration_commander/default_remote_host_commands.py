from remote_host_command.public import RemoteHostCommand


class DefaultRemoteHostCommand():
    ADD_FSTAB_ENTRY = RemoteHostCommand(
        'sudo echo -e "{IDENTIFIER}\t{MOUNTPOINT}\t{FILESYSTEM}\tdefaults\t0\t2" >> /etc/fstab'
    )
    RELOAD_MOUNTS = RemoteHostCommand('sudo mount -a')