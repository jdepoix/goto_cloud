import os
from io import BytesIO


class VmMock(object):
    def __init__(self, commands, expected_config):
        self.commands = commands
        self.expected_config = expected_config

    def execute(self, command):
        actual_command = next((known_command for known_command in self.commands if known_command in command), None)

        return (
            (BytesIO(), BytesIO(self.commands[actual_command].encode()), BytesIO())
            if actual_command
            else (BytesIO(), BytesIO(), BytesIO(b'Command does not exist!'))
        )

    def get_config(self):
        return self.expected_config

    @staticmethod
    def create_from_file(
        commands_root_directory_path,
        filename,
        command_directory_map,
        expected_config,
    ):
        commands_root_directory = os.path.realpath(commands_root_directory_path)
        commands = {}

        for command in command_directory_map:
            with open(
                os.path.join(os.path.join(commands_root_directory, command_directory_map[command]), filename)
            ) as command_output:
                commands[command] = command_output.read()
        return VmMock(commands, expected_config)
