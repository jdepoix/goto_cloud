from abc import ABCMeta, abstractmethod

from operating_system.public import OperatingSystem

from operating_system_support.public import AbstractedRemoteHostOperator

from remote_execution.public import RemoteHostExecutor


class SystemInfoGetter(metaclass=ABCMeta):
    """
    takes care of retrieving the system information for a given system
    """
    def __init__(self, remote_executor):
        """
        is initialized with a given RemoteExecutor
        :param remote_executor: the remote executor the commands are executed by
        :type remote_executor: remote_execution.public.RemoteExecutor 
        
        """
        self.remote_executor = remote_executor

    @abstractmethod
    def get_block_devices(self):
        """
        retrieves information about the systems block devices
        
        :return: block device info
        :rtype: dict
        """
        pass

    def get_hardware(self):
        """
        retrieves information about the systems hardware 

        :return: hardware info
        :rtype: dict
        """
        return {
            'cpus': self.get_cpus(),
            'ram': self.get_ram(),
        }

    @abstractmethod
    def get_cpus(self):
        """
        retrieves information about the systems cpus

        :return: cpu info
        :rtype: dict
        """
        pass

    @abstractmethod
    def get_ram(self):
        """
        retrieves information about the systems ram

        :return: ram info
        :rtype: dict
        """
        pass

    def get_network_info(self):
        """
        retrieves information about the systems network 

        :return: network info
        :rtype: dict
        """
        return {
            'hostname': self.get_hostname(),
            'interfaces': self.get_network_interfaces()
        }

    @abstractmethod
    def get_hostname(self):
        """
        retrieves the systems hostname

        :return: hostname
        :rtype: str
        """
        pass

    @abstractmethod
    def get_network_interfaces(self):
        """
        retrieves information about the systems network interfaces

        :return: network interface info
        :rtype: dict
        """
        pass

    @abstractmethod
    def get_routes(self):
        """
        retrieves information about the systems routes
        
        :return: routes
        :rtype: dict
        """
        pass

    @abstractmethod
    def get_os(self):
        """
        retrieves information about the systems operating system
    
        :return: operating system info
        :rtype: dict
        """
        pass

    def get_system_info(self):
        """
        retrieves aggregates information about the system

        :return: system info
        :rtype: dict
        """
        return {
            'block_devices': self.get_block_devices(),
            'network': self.get_network_info(),
            'os': self.get_os(),
            'hardware': self.get_hardware(),
        }


class DebianSystemInfoGetter(SystemInfoGetter):
    """
    SystemInfoGetter implementation for Debian based systems
    """
    class Command():
        """
        Commands which are executed to retrieved the relevant information
        """
        CPU_INFO = 'cat /proc/cpuinfo'
        FDISK = 'sudo fdisk -l {devices}'
        HOSTNAME = 'hostname'
        IFCONFIG = 'ifconfig'
        LSBLK = 'lsblk -bPo NAME,FSTYPE,LABEL,UUID,MOUNTPOINT,TYPE,SIZE'
        LSBLK_TREE = 'lsblk -no NAME'
        MEM_INFO = 'cat /proc/meminfo | grep MemTotal:'
        OS_RELEASE = 'cat /etc/os-release'
        ROUTE = 'route -n'

    def _get_unordered_block_devices(self):
        unordered_devices = {}

        for line in self.remote_executor.execute(self.Command.LSBLK).split('\n'):
            device_info = {}

            for entry in line.split():
                key, value = entry.split('=')
                device_info[key] = value.strip('"')

            unordered_devices[device_info['NAME']] = {
                'type': device_info['TYPE'],
                'fs': device_info['FSTYPE'],
                'uuid': device_info['UUID'],
                'label': device_info['LABEL'],
                'mountpoint': device_info['MOUNTPOINT'],
                'size': int(device_info['SIZE']),
            }

        return unordered_devices

    def _get_block_device_dependencies(self):
        STEP = 2
        block_device_dependencies = {}
        last_visited_per_level = {}

        for line in self.remote_executor.execute(self.Command.LSBLK_TREE).split('\n'):
            indentation = next(index for index, char in enumerate(line) if char.isalpha())
            device = line[indentation:]

            block_device_dependencies[device] = {
                'children': [],
                'level': indentation / STEP,
            }
            last_visited_per_level[indentation] = device

            parent_level = indentation - STEP

            if parent_level >= 0 and parent_level in last_visited_per_level:
                block_device_dependencies[last_visited_per_level[parent_level]]['children'].append(device)

        return block_device_dependencies

    def _get_partition_info(self, disks):
        partitions = {}

        for section in self.remote_executor.execute(
            self.Command.FDISK.format(devices=' '.join('/dev/{disk}'.format(disk=disk) for disk in disks))
        ).split('Disk /')[1:]:
            if 'Device' in section:
                for partition_info_line in (line for line in section[section.index('Device'):].split('\n')[1:] if line):
                    partition_info = partition_info_line.split()
                    device = partition_info[0].split('/')[-1]
                    partitions[device] = {}

                    if partition_info[1] == '*':
                        partitions[device]['bootable'] = True
                        partition_size_info_base_index = 2
                    else:
                        partitions[device]['bootable'] = False
                        partition_size_info_base_index = 1

                    partitions[device]['start'] = int(partition_info[partition_size_info_base_index])
                    partitions[device]['end'] = int(partition_info[partition_size_info_base_index + 1])

        return partitions

    def _build_block_device_tree(self, root_device, unordered_devices, partition_info, device_dependencies):
        device_info = unordered_devices[root_device].copy()

        if root_device in partition_info:
            device_info.update(partition_info[root_device].copy())

        device_info['children'] = {
            child: self._build_block_device_tree(child, unordered_devices, partition_info, device_dependencies)
            for child in device_dependencies[root_device]['children']
        }

        return device_info

    def get_block_devices(self):
        block_device_dependencies = self._get_block_device_dependencies()
        unordered_devices = self._get_unordered_block_devices()
        partition_info = self._get_partition_info(
            [device for device in unordered_devices if unordered_devices[device]['type'] == 'disk']
        )

        return {
            device: self._build_block_device_tree(
                device,
                unordered_devices,
                partition_info,
                block_device_dependencies
            )
            for device in (
                root_device for root_device in block_device_dependencies
                if block_device_dependencies[root_device]['level'] == 0
            )
        }

    def get_cpus(self):
        cpus_info = []

        for cpu_info_section in self.remote_executor.execute(self.Command.CPU_INFO).split('\n\n'):
            cpu_info = {}

            for line in cpu_info_section.split('\n'):
                key, value = (item.strip() for item in line.split(':'))

                if key == 'model name':
                    cpu_info['model'] = value
                elif key == 'cpu MHz':
                    cpu_info['mhz'] = float(value)

            if cpu_info:
                cpus_info.append(cpu_info)

        return cpus_info

    def get_ram(self):
        return {
            'size': int(self.remote_executor.execute(self.Command.MEM_INFO).split()[1]) * 1000
        }

    def get_hostname(self):
        return self.remote_executor.execute(self.Command.HOSTNAME)

    def get_network_interfaces(self):
        network_info = {}

        routes = self.get_routes()

        for interface_config in self.remote_executor.execute(self.Command.IFCONFIG).split('\n\n'):
            config_lines = interface_config.split('\n')

            interface = config_lines[0].split()[0]

            network_info[interface] = {}

            for ip_config in config_lines[1].split()[1:]:
                key, value = ip_config.split(':')

                if key == 'addr':
                    network_info[interface]['ip'] = value
                elif key == 'Mask':
                    network_info[interface]['net_mask'] = value

            network_info[interface]['routes'] = routes[interface] if interface in routes else []

        return network_info

    def get_routes(self):
        routes = {}

        for line in self.remote_executor.execute(self.Command.ROUTE).split('\n')[2:]:
            columns = line.split()
            route = {
                'net': columns[0],
                'gateway': columns[1],
                'net_mask': columns[2],
            }

            if columns[7] in routes:
                routes[columns[7]].append(route)
            else:
                routes[columns[7]] = [route]

        return routes

    def get_os(self):
        os_info = {}

        for line in self.remote_executor.execute(self.Command.OS_RELEASE).split('\n'):
            key, value = line.split('=')

            if key == 'NAME':
                os_info['name'] = value.strip('"')
            elif key == 'VERSION_ID':
                os_info['version'] = value.strip('"')

        return os_info


class RemoteHostSystemInfoGetter(AbstractedRemoteHostOperator):
    def _get_operating_systems_to_supported_operation_mapping(self):
        return {
            (OperatingSystem.DEBIAN,): DebianSystemInfoGetter
        }

    def _init_operator_class(self, operator_class):
        return operator_class(RemoteHostExecutor(self.remote_host))

    def get_block_devices(self):
        return self.operator.get_block_devices()

    def get_hardware(self):
        return self.operator.get_hardware()

    def get_cpus(self):
        return self.operator.get_cpus()

    def get_ram(self):
        return self.operator.get_ram()

    def get_network_info(self):
        return self.operator.get_network_info()

    def get_hostname(self):
        return self.operator.get_hostname()

    def get_network_interfaces(self):
        return self.operator.get_network_interfaces()

    def get_os(self):
        return self.operator.get_os()

    def get_system_info(self):
        return self.operator.get_system_info()
