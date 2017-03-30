from abc import ABCMeta, abstractclassmethod

from dict_utils.public import DictUtils
from operating_system.public import OperatingSystem


class OperatingSystemRelations():
    _RELATIONS = {
        OperatingSystem.LINUX: {
            OperatingSystem.DEBIAN: OperatingSystem.UBUNTU
        }
    }
    """
    Represents the relations between operating systems. This mainly is to represent how different Linux distributions
    are connected. This way something which is supported by a Debian system, is also evaluated as supported by a Ubuntu
    system.
    """

    @classmethod
    def get_subsystems(cls, operating_system):
        """
        returns the operating systems, which the given operating system is related parent to
        
        :param operating_system: the operating system which is the parent
        :type operating_system: str
        :return: list of subsystems
        :rtype: list
        """
        subsystems = DictUtils.find_sub_dict_by_key(cls._RELATIONS, operating_system)
        return DictUtils.flatten_child_elements(subsystems) if subsystems else None


class PartiallySupported(metaclass=ABCMeta):
    """
    represents a class which is only supported by limited operating systems
    """
    @classmethod
    def is_supported(cls, operating_system):
        """
        checks if the given operating system is supported
        
        :param operating_system: the operating system to check support for
        :type operating_system: str
        :return: if it is supported or not
        :rtype: bool
        """
        supported_systems = cls._get_supported_operating_systems()

        return (
            operating_system in supported_systems
            or any(
                operating_system in OperatingSystemRelations.get_subsystems(supported_system)
                for supported_system in supported_systems
            )
        )

    @abstractclassmethod
    def _get_supported_operating_systems(cls):
        """
        
        :return: a tuple of supported operating systems
        :rtype: (str,)
        """
        pass
