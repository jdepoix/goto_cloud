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
        self.source = source

    def resolve(self, path):
        """
        resolves the given path to the corresponding path on the target 
        
        :param path: path to resolve
        :type path: str
        :return: the resolved path
        :rtype: str
        """
        if len(path) < 1 or path[0] != '/':
            raise SourceFileLocationResolver.InvalidPathException(
                'The path {path} is invalid. Relative paths are not allowed'.format(
                    path=path
                )
            )

        mountpoints = self._get_mountpoint_mapping()
        best_matching_mountpoint = self._find_best_matching_root_folder(set(mountpoints.keys()), path)
        path_relative_to_mountpoint = path[len(best_matching_mountpoint):]

        return '{mountpoint}{path}'.format(
            mountpoint=mountpoints[best_matching_mountpoint],
            path=('/' + path_relative_to_mountpoint)
                if path_relative_to_mountpoint and path_relative_to_mountpoint[0] != '/'
                else path_relative_to_mountpoint
        )

    def _get_mountpoint_mapping(self):
        """
        
        :return: the flatted mapping of source mountpoints onto the target devices mountpoints  
        :rtype: dict
        """
        mountpoint_mapping = {}

        for device_id, device in self.source.target.device_mapping.items():
            device_mountpoint = self.source.remote_host.system_info['block_devices'][device_id]['mountpoint']

            if device_mountpoint:
                mountpoint_mapping[device_mountpoint] = device['mountpoint']

            for partiton_id, partiton in device['children'].items():
                partition_mountpoint = self.source.remote_host.system_info[
                    'block_devices'
                ][
                    device_id
                ][
                    'children'
                ][
                    partiton_id
                ][
                    'mountpoint'
                ]

                if partition_mountpoint:
                    mountpoint_mapping[partition_mountpoint] = partiton['mountpoint']

        return mountpoint_mapping

    def _find_best_matching_root_folder(self, roots, path):
        """
        finds the root folder which is closed to the given path
        
        :param roots: a iterable of possible root folders
        :type roots: set
        :param path: the path which should be matched
        :type path: str
        :return: the root folder which matches best
        :rtype: str
        """
        matching_roots = []

        for root in roots:
            if path.startswith(root):
                matching_roots.append(root)

        if not matching_roots:
            raise SourceFileLocationResolver.InvalidPathException(
                'No root mountpoint was found! This should never happen!'
            )

        return max(matching_roots, key=lambda x: len(x))
