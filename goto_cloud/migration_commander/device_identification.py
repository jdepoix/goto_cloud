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

    def _execute(self):
        self._target.device_mapping = self._map_unallocated_devices_onto_source_devices(
            self._get_unallocated_target_devices()
        )
        self._target.save()

    def _handle_error_report(self, error_report):
        raise DeviceIdentificationCommand.NoMatchingDevicesException(
            'While trying to match the target and source devices, the following errors occurred. Please resolves these '
            'manually and then skip this step:\n{errors}'.format(errors=error_report)
        )

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
            if unallocated_devices:
                matching_device_id = next(
                    (
                        target_device_id
                        for target_device_id, target_device
                        in unallocated_devices.items() if target_device['size'] == source_device['size']
                    ),
                    None
                )

                if matching_device_id:
                    device_map[source_device_id] = {
                        'id': matching_device_id,
                        'mountpoint': self._map_mountpoint(source_device),
                        'children': self._map_children(source_device_id, matching_device_id)
                    }

                    del unallocated_devices[matching_device_id]
                else:
                    self._add_error(
                        'no device of the target system matches the size of {source_device_id} on the source system'
                        .format(
                            source_device_id=source_device_id
                        )
                    )
            else:
                self._add_error(
                    'there are not enough devices on the target instance, to be able to replicated the source'
                )

        return device_map

    def _map_children(self, source_device_id, target_device_id):
        """
        maps the children of the source device to children in the target device
        
        :param source_device_id: the id of the source device
        :type source_device_id: str
        :param target_device_id: the id of the target device
        :type target_device_id: str
        :return: the children of the target device
        :rtype: dict
        """
        children = {}
        source_device = self._source.remote_host.system_info['block_devices'][source_device_id]

        for partition_device_id, partition_device in source_device['children'].items():
            children[partition_device_id] = {
                'id': target_device_id + partition_device_id[-1],
                'mountpoint': self._map_mountpoint(partition_device)
            }

        return children

    def _map_mountpoint(self, device):
        """
        map the mountpoint of the device to a hashed mountpoint
        
        :param device: device to hash the mountpoint for
        :type device: dict
        :return: the mountpoint containing the hashed path
        :rtype: str
        """
        return '/mnt/{mountpoint_hash}'.format(
            mountpoint_hash=str(hash(device['mountpoint']))
        ) if device['mountpoint'] else ''
