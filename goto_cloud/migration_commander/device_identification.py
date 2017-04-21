from command.public import SourceCommand


class DeviceIdentificationCommand(SourceCommand):
    """
    takes care of identifying, which of the targets devices, should replicated, which device of the source system
    """
    class NoMatchingDevicesException(Exception):
        """
        raised if no matching devices were found
        """
        pass

    def execute(self):
        self._target.device_mapping = self._map_unallocated_devices_onto_source_devices(
            self._get_unallocated_target_devices()
        )
        self._target.save()

    def _get_unallocated_target_devices(self):
        """
        gets the devices from target, which have not been allocated
        
        :return: unallocated target devices
        :rtype: dict
        """
        return {
            target_device_id: target_device
            for target_device_id, target_device in self._target.remote_host.system_info['block_devices'].items()
            if not target_device['fs'] and not target_device['children']
        }

    def _map_unallocated_devices_onto_source_devices(self, unallocated_devices):
        """
        maps the unallocated target device on the source devices, which they will replicate during the migration
        
        :param unallocated_devices: the unallocated devices
        :type unallocated_devices: dict
        :return: the mapped devices
        :rtype: dict
        """
        device_map = {}

        for source_device_id, source_device in self._source.remote_host.system_info['block_devices'].items():
            if not unallocated_devices:
                raise DeviceIdentificationCommand.NoMatchingDevicesException(
                    'there are not enough devices on the target instance, to be able to replicated the source'
                )

            matching_device = next(
                (
                    target_device_id
                    for target_device_id, target_device
                    in unallocated_devices.items() if target_device['size'] == source_device['size']
                ),
                None
            )

            if not matching_device:
                raise DeviceIdentificationCommand.NoMatchingDevicesException(
                    'no device of the target system matches the size of {source_device_id} on the source system'.format(
                        source_device_id=source_device_id
                    )
                )

            device_map[matching_device] = source_device_id

            del unallocated_devices[matching_device]

        return device_map
