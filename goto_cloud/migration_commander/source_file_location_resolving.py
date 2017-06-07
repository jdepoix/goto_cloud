class SourceFileLocationResolver():
    """
    takes care of resolving which the new path of a file on the source is, on the targets mapped devices
    """
    class InvalidPathException(Exception):
        """
        raised if a given path is not valid
        """
        pass

    def __init__(self, source):
        """
        :param source: the source the paths should be resolved for
        :type source: source.public.Source
        """
        self._source = source
        self._mountpoint_mapping = self._get_mountpoint_mapping()

    def resolve_path(self, path):
        """
        resolves the given path to the corresponding path on the target 
        
        :param path: path to resolve
        :type path: str
        :return: the resolved path
        :rtype: str
        """
        best_matching_mountpoint = self._find_best_matching_root_folder(path)
        path_relative_to_mountpoint = path[len(best_matching_mountpoint):]

        return '{mountpoint}{path}'.format(
            mountpoint=self._mountpoint_mapping[best_matching_mountpoint]['mountpoint'],
            path=('/' + path_relative_to_mountpoint)
                if path_relative_to_mountpoint and path_relative_to_mountpoint[0] != '/'
                else path_relative_to_mountpoint
        )

    def resolve_device(self, path):
        """
        resolves the given path to the corresponding device on the target

        :param path: path to resolve
        :type path: str
        :return: the device id of the device the path translates to on the target machine
        :rtype: str
        """
        best_matching_mountpoint = self._find_best_matching_root_folder(path)
        return self._mountpoint_mapping[best_matching_mountpoint]['device_id']

    def resolve_disk(self, path):
        """
        resolves which disk the given path is on

        :param path: path to resolve
        :type path: str
        :return: device id of the the disk the given path translates to on the target machine
        :rtype: str
        """
        matching_device_id = self.resolve_device(path)

        for device in self._source.target.device_mapping.values():
            if device['id'] == matching_device_id:
                return device['id']
            for partition in device['children'].values():
                if partition['id'] == matching_device_id:
                    return device['id']

    def _validate_path(self, path):
        """
        validates the given path and raises an InvalidPathException in case it is invalid

        :param path: the path to validate
        :type path: str
        """
        if len(path) < 1 or path[0] != '/':
            raise SourceFileLocationResolver.InvalidPathException(
                'The path {path} is invalid. Relative paths are not allowed'.format(
                    path=path
                )
            )

    def _get_mountpoint_mapping(self):
        """
        
        :return: the flatted mapping of source mountpoints onto the target devices mountpoints  
        :rtype: dict
        """
        mountpoint_mapping = {}

        for device_id, device in self._source.target.device_mapping.items():
            device_mountpoint = self._source.remote_host.system_info['block_devices'][device_id]['mountpoint']

            if device_mountpoint:
                mountpoint_mapping[device_mountpoint] = {
                    'device_id': device['id'],
                    'mountpoint': device['mountpoint'],
                }

            for partition_id, partition in device['children'].items():
                partition_mountpoint = self._source.remote_host.system_info[
                    'block_devices'
                ][
                    device_id
                ][
                    'children'
                ][
                    partition_id
                ][
                    'mountpoint'
                ]

                if partition_mountpoint:
                    mountpoint_mapping[partition_mountpoint] = {
                        'device_id': partition['id'],
                        'mountpoint': partition['mountpoint'],
                    }

        return mountpoint_mapping

    def _find_best_matching_root_folder(self, path):
        """
        finds the root folder which is closed to the given path
        
        :param path: the path which should be matched
        :type path: str
        :return: the root folder which matches best
        :rtype: str
        """
        self._validate_path(path)
        self._mountpoint_mapping = self._get_mountpoint_mapping()

        matching_roots = []

        for root in set(source_mountpoint for source_mountpoint, target_mountpoint in self._mountpoint_mapping.items()):
            if path.startswith(root):
                matching_roots.append(root)

        if not matching_roots:
            raise SourceFileLocationResolver.InvalidPathException(
                'No root mountpoint was found! This should never happen!'
            )

        return max(matching_roots, key=lambda x: len(x))
