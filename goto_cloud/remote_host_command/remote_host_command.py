class RemoteHostCommand():
    """
    can be used to wrap a command which can be execute on a Remote Host
    """
    class InvalidContextException(Exception):
        """
        raised, if the context provided for rendering a RemoteHostCommand, is not valid
        """
        def __init__(self, command, context):
            super().__init__(
                'The following command, could not be resolved, with the given context:'
                '\n{command}\n\ncontext:\n{context}'.format(
                    command=str(command),
                    context=str(context),
                )
            )

    def __init__(self, command):
        """
        Initialized with the command which will be rendered. This can either be a string, or a dict looking like this:
        {
            'command': str,
            'optionals' {
                str: str,
                ...
            }
        }
        if the command is a dict (and therefore optionals are provided), the optional parts will be rendered into the 
        command, if the key of the optional if provided for rendering
        
        :param command: the command to render at execution
        :type command: str | dict
        """
        if isinstance(command, dict):
            self.command = command['command']
            self.optionals = command['optionals']
        else:
            self.command = command
            self.optionals = {}

    def render(self, **context):
        """
        renders the command with the given context
        
        :param context: the context to render the command with
        :type context: **dict
        :return: the rendered command
        :rtype: str
        """
        if self.optionals:
            optional_strings = []

            for relevant_optional in (optional for optional in self.optionals if optional in context):
                optional_strings.append(
                    self.optionals[relevant_optional].format(**{relevant_optional.upper(): context[relevant_optional]})
                )
                del context[relevant_optional]

            context['optionals'] = ' '.join(optional_strings)
        try:
            return self.command.format(**{key.upper(): value for key, value in context.items()})
        except KeyError:
            raise RemoteHostCommand.InvalidContextException(self.command, context)
