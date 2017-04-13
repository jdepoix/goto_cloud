from remote_host.public import RemoteHost

from source.public import Source

from system_info_inspection.public import RemoteHostSystemInfoGetter

from target.public import Target

from .db_item_handling import DbItemHandler
from .blueprint_resolving import BlueprintResolver


class SourceParser(DbItemHandler):
    """
    Takes care of parsing the source provided by a migration plan.
    
    It creates the db entry and also takes care of resolving the associated blueprint, which is used to create the
    target.
    """
    class InvalidSourceException(Exception):
        """
        is raised if a source config is not valid
        """
        pass

    def __init__(self, blueprints):
        """
        :param blueprints: the blueprints which should be used to resolve the sources blueprints
        :type blueprints: dict
        """
        super().__init__()
        self._blueprint_resolver = BlueprintResolver(blueprints)

    def parse(self, source):
        """
        parses the given source using the provided blueprints
        
        :param source: the source to parse
        :type source: dict
        :return: the created Source
        :rtype: Source
        """
        try:
            blueprint = self._resolve_blueprint(source)
            remote_host = self._create_remote_host(source, blueprint)
            system_info = self._get_system_info(remote_host)
            self._update_remote_host_with_system_info(remote_host, system_info)
            target = self._create_target(blueprint)
            return self._create_source(remote_host, target)
        except KeyError:
            raise SourceParser.InvalidSourceException(
                'the source: {address} is not valid'.format(address=source.get('address', source))
            )

    def _create_remote_host(self, source, blueprint):
        """
        creates the RemoteHost db entry
        
        :param source: the source to use
        :type source: dict
        :param blueprint: the blueprint to use
        :type blueprint: dict
        :return: the newly created remote host
        :rtype: RemoteHost
        """
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
        """
        retrieves the system info for a given remote host
        
        :param remote_host: the remote host to get the system info for
        :type remote_host: RemoteHost
        :return: the retrieved system info
        :rtype: dict
        """
        return RemoteHostSystemInfoGetter(remote_host).get_system_info()

    def _create_source(self, remote_host, target):
        """
        creates the source db entry
        
        :param remote_host: the remote host which is used to connect to the source
        :type remote_host: RemoteHost
        :param target: the target which the source translates to
        :type target: Target
        :return: the newly created source
        :rtype: Source
        """
        return self.add_db_item(
            Source.objects.create(
                target=target,
                remote_host=remote_host,
            )
        )

    def _update_remote_host_with_system_info(self, remote_host, system_info):
        """
        updates the remote host data, using the retrieved system info
        
        :param remote_host: the remote host to update
        :type remote_host: RemoteHost
        :param system_info: the system info used to update the remote host data
        :type system_info: dict
        """
        remote_host.system_info = system_info
        remote_host.os = system_info['os']['name']
        remote_host.version = system_info['os']['version']
        remote_host.save()

    def _create_target(self, blueprint):
        """
        creates a target db entry, using a provided blueprint
        
        :param blueprint: the resolved blueprint to create the target with
        :type blueprint: dict
        :return: the newly created target
        :rtype: Target
        """
        return self.add_db_item(Target.objects.create(blueprint=blueprint))

    def _resolve_blueprint(self, source):
        """
        resolves the blueprint for a given source
        
        :param source: the source to resolve the blueprint for 
        :type source: dict
        :return: the resolved blueprint 
        :rtype: dict
        """
        return self._blueprint_resolver.resolve(source['blueprint'])
