from commander.public import Commander

from source.public import Source

from .cloud_commanding import \
    CreateTargetCommand, \
    StopTargetCommand, \
    DeleteBootstrapNetworkInterfaceCommand, \
    DeleteBootstrapVolumeCommand, \
    ConfigureBootDeviceCommand, \
    StartTargetCommand
from .target_system_info_inspection import GetTargetSystemInfoCommand
from .device_identification import DeviceIdentificationCommand
from .partition_creation import CreatePartitionsCommand
from .filesystem_creation import CreateFilesystemsCommand
from .filesystem_mounting import FilesystemMountCommand
from .syncing import SyncCommand, FinalSyncCommand
from .config_adjustment import NetworkConfigAdjustmentCommand, SshConfigAdjustmentCommand, FstabAdjustmentCommand
from .bootloader_reinstallation import BootloaderReinstallationCommand


class MigrationCommander(Commander):
    _COMMAND_DRIVER = {
        Source.Status.CREATE_TARGET: CreateTargetCommand,
        Source.Status.GET_TARGET_SYSTEM_INFORMATION: GetTargetSystemInfoCommand,
        Source.Status.IDENTIFY_DEVICES: DeviceIdentificationCommand,
        Source.Status.CREATE_PARTITIONS: CreatePartitionsCommand,
        Source.Status.CREATE_FILESYSTEMS: CreateFilesystemsCommand,
        Source.Status.MOUNT_FILESYSTEMS: FilesystemMountCommand,
        Source.Status.SYNC: SyncCommand,
        Source.Status.FINAL_SYNC: FinalSyncCommand,
        Source.Status.ADJUST_NETWORK_CONFIG: NetworkConfigAdjustmentCommand,
        Source.Status.ADJUST_SSH_CONFIG: SshConfigAdjustmentCommand,
        Source.Status.ADJUST_FSTAB: FstabAdjustmentCommand,
        Source.Status.REINSTALL_BOOTLOADER: BootloaderReinstallationCommand,
        Source.Status.STOP_TARGET: StopTargetCommand,
        Source.Status.DELETE_BOOTSTRAP_VOLUME: DeleteBootstrapVolumeCommand,
        Source.Status.DELETE_BOOTSTRAP_NETWORK_INTERFACE: DeleteBootstrapNetworkInterfaceCommand,
        Source.Status.CONFIGURE_BOOT_DEVICE: ConfigureBootDeviceCommand,
        Source.Status.START_TARGET: StartTargetCommand,
    }

    @property
    def _commander_driver(self):
        return self._COMMAND_DRIVER
