import sys


class MountpointMapper(object):
    @staticmethod
    def map_mountpoint(parent_directory, mountpoint):
        """
        maps a mountpoint onto a hashed directory name
        
        :param parent_directory: the directory the mapped directory should reside in
        :type parent_directory: str
        :param mountpoint: the mountpoint which will be mapped
        :type mountpoint: str
        :return: the mapped mountpoint
        :rtype: str
        """
        return '{parent_directory}{mountpoint_hash}'.format(
            parent_directory=''
                            if not parent_directory
                            else (parent_directory + '/' if parent_directory[-1] != '/' else parent_directory),
            mountpoint_hash=str(hash(mountpoint) + sys.maxsize + 1)
        )
