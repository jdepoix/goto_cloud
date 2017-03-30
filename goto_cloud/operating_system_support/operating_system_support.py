from abc import ABCMeta, abstractmethod

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
    def is_supported(self, operating_system):
        """
        checks if the given operating system is supported
        
        :param operating_system: the operating system to check support for
        :type operating_system: str
        :return: if it is supported or not
        :rtype: bool
        """
        related_systems = OperatingSystemRelations.get_subsystems(operating_system)

        return (
            operating_system in self._supported_operating_systems
            or any(
                supported_system in related_systems
                for supported_system in self._supported_operating_systems
            )
        )

    @property
    @abstractmethod
    def _supported_operating_systems(self):
        """
        
        :return: a tuple of supported operating systems
        :rtype: (str,)
        """
        pass
