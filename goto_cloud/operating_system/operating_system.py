from enums.public import StringEnum


class OperatingSystem(StringEnum):
    class NotSupportedException(Exception):
        """
        is thrown if a given operating system is not supported
        """
        pass

    LINUX = 'Linux'
    DEBIAN = 'Debian'
    UBUNTU = 'Ubuntu'
    WINDOWS = 'Windows'
