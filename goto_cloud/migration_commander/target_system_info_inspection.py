from command.command import SourceCommand


class GetTargetSystemInfoCommand(SourceCommand):
    """
    Takes care of providing the target with system information after it has been created
    """
    def _execute(self):
        self._source.target.remote_host.update_system_info()
