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

    def __init__(self, operating_system):
        """
        
        :param operating_system: the operating system, on whom's relations you want to work
        :type operating_system: str  
        """
        self.operating_system = operating_system

    def is_parent_of(self, related_operating_system):
        """
        checks if this operating system is parent of the given operating system
        
        :param related_operating_system: the related operating system
        :type related_operating_system: str
        :return: whether it is a parent or not
        :rtype: bool
        """
        return related_operating_system in self.get_subsystems()

    def is_child_of(self, related_operating_system):
        """
        checks if this operating system is child of the given operating system

        :param related_operating_system: the related operating system
        :type related_operating_system: str
        :return: whether it is a child or not
        :rtype: bool
        """
        return self.operating_system in OperatingSystemRelations(related_operating_system).get_subsystems()

    def get_subsystems(self):
        """
        returns the operating systems, which the given operating system is related parent to
        
        :return: list of subsystems
        :rtype: list
        """
        subsystems = DictUtils.find_sub_dict_by_key(self._RELATIONS, self.operating_system)
        return DictUtils.flatten_child_elements(subsystems) if subsystems else []


class AbstractedRemoteHostOperator(metaclass=ABCMeta):
    """
    a operation which executes on a given RemoteHost and abstracts the operating system support away
    """
    def __init__(self, remote_host):
        self.remote_host = remote_host
        self.operator = self._get_supported_operator()

    def _get_supported_operator(self):
        """
        returns the supported operator class for a given RemoteHost  
        
        :return: a operator class, which is supported by the given RemoteHost
        :rtype: Any.__class__
        :raises OperatingSystem.NotSupportedException: raised in case, the operating system of the given RemoteHost is
        not supported at all
        """
        supported_operator = self._get_directly_supported_operator()

        if supported_operator:
            return supported_operator

        related_supported_operator = self._get_related_supported_operator()

        if related_supported_operator:
            return related_supported_operator

        raise OperatingSystem.NotSupportedException()


    def _get_directly_supported_operator(self):
        for operating_systems, operator_class in self._get_operating_systems_to_supported_operation_mapping().items():
            if self.remote_host.os in operating_systems:
                return self._init_operator_class(operator_class)
        return None

    def _get_related_supported_operator(self):
        for operating_systems, operator_class in self._get_operating_systems_to_supported_operation_mapping().items():
            remote_host_operating_system_relations = OperatingSystemRelations(self.remote_host.os)
            if any(
                remote_host_operating_system_relations.is_child_of(operating_system)
                for operating_system in operating_systems
            ):
                return self._init_operator_class(operator_class)
        return None

    @abstractmethod
    def _get_operating_systems_to_supported_operation_mapping(self):
        """

        :return: maps a tuple of operating systems, onto the operation classes, which support it
        :rtype: {(str,): Any}
        """
        pass

    @abstractmethod
    def _init_operator_class(self, operator_class):
        """
        initializes the supported operator class
        
        :param operator_class: the operator class
        :type operator_class: Any.__class__
        :return: an instance of the operator class
        :rtype: Any
        """
        pass
