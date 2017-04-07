from remote_host.public import RemoteHost

from source.public import Source

from system_info_inspection.public import RemoteHostSystemInfoGetter

from target.public import Target

from .db_item_handling import DbItemHandler
from .blueprint_resolving import BlueprintResolver


class SourceParser(DbItemHandler):
    class InvalidSourceException(Exception):
        """
        is raised if a source config is not valid
        """
        pass

    def __init__(self, blueprints):
        super().__init__()
        self._blueprint_resolver = BlueprintResolver(blueprints)

    def parse(self, source):
        try:
            blueprint = self._resolve_blueprint(source)
            remote_host = self._create_remote_host(source, blueprint)
            system_info = self._get_system_info(remote_host)
            self._update_remote_host_system_info(remote_host, system_info)
            target = self._create_target(blueprint)
            return self._create_source(remote_host, system_info, target)
        except KeyError:
            raise SourceParser.InvalidSourceException(
                'the source: {address} is not valid'.format(address=source.get('address', source))
            )

    def _create_remote_host(self, source, blueprint):
        return self.add_db_item(
            RemoteHost.objects.create(
                address=source['address'],
                port=blueprint['ssh'].get('port'),
                username=blueprint['ssh'].get('username'),
                password=blueprint['ssh'].get('password'),
                private_key=blueprint['ssh'].get('private_key'),
                private_key_file_path=blueprint['ssh'].get('private_key_file_path'),
            )
        )

    def _get_system_info(self, remote_host):
        return RemoteHostSystemInfoGetter(remote_host).get_system_info()

    def _create_source(self, remote_host, system_info, target):
        return self.add_db_item(
            Source.objects.create(
                target=target,
                system_info=system_info,
                remote_host=remote_host,
            )
        )

    def _update_remote_host_system_info(self, remote_host, system_info):
        remote_host.os = system_info['os']['name']
        remote_host.version = system_info['os']['version']
        remote_host.save()

    def _create_target(self, blueprint):
        return self.add_db_item(Target.objects.create(blueprint=blueprint))

    def _resolve_blueprint(self, source):
        return self._blueprint_resolver.resolve(source['blueprint'])
