from command.command import SourceCommand
from system_info_inspection.system_info_inspection import RemoteHostSystemInfoGetter


class GetTargetSystemInfoCommand(SourceCommand):
    """
    Takes care of providing the target with system information after it has been created
    """
    def _execute(self):
        target_remote_host = self._source.target.remote_host
        target_remote_host.system_info = RemoteHostSystemInfoGetter(target_remote_host).get_system_info()
        target_remote_host.save()
