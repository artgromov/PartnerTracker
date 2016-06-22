import logging

logger = logging.getLogger(__name__)


class Mode:
    def __init__(self, prompt, root=False):
        self.prompt = prompt
        self.root = root

        self.help_command_width = None
        self.help_argument_width = None
        self.help_description_help = 'Display this message'
        if root:
            self.help_description_exit = 'Exit from the program.'
        else:
            self.help_description_exit = 'Exit from current mode.'

        self.namespace = []

    def add_command(self, command, callback, index=None):
        """
        Appends (command, callback) tuple to mode namespace.
        If index given an integer, uses insert instead of append.
        Replaces callback in case of command match.

        Callback should support only one string argument.
        Command help uses callback's docstring, argument help uses annotations without any modifications.
        """

        commands = (i[0] for i in self.namespace)
        if command not in commands:
            if isinstance(index, int):
                self.namespace.insert(index, (command, callback))
            else:
                self.namespace.append((command, callback))
        else:
            index = self.remove_command(command)
            self.namespace.insert(index, (command, callback))

    def remove_command(self, command):
        try:
            index, callback = self.lookup_command(command)
        except KeyError:
            logger.error('no such command: %s' % command)
        else:
            self.namespace.pop(index)
            return index

    def __call__(self):
        while True:
            command, argument = self.get_user_input()
            try:
                index, callback = self.lookup_command(command)
                logger.debug('calling %s callback' % callback)
                callback(argument)
            except KeyError:    # no user callback found, call internal commands
                if command == 'help':
                    self.print_usage()
                elif command == 'exit':
                    break
                else:
                    print('Unrecognized command: %s' % command)

    def get_user_input(self):
        user_input = input(self.prompt).strip()
        command = user_input.split(' ')[0]
        argument = ' '.join(user_input.split(' ')[1:])
        logger.debug('got command: "{}", argument: "{}"'.format(command, argument))
        return command, argument

    def lookup_command(self, command_name):
        for index, (command, callback) in enumerate(self.namespace):
            if command == command_name:
                return index, callback
        raise KeyError

    def print_usage(self):
        command_width = 4
        argument_width = len(self.help_description_exit)
        lines = []
        for command, callback in self.namespace:
            if command_width < len(command):
                command_width = len(command)

            if callback.__annotations__:
                argument = '[' + list(callback.__annotations__.values())[0] + ']'
                if argument_width < len(argument):
                    argument_width = len(argument)
            else:
                argument = ''

            if callback.__doc__:
                description = callback.__doc__.replace('\n', ' ')
            else:
                description = ''

            lines.append((command, argument, description))

        logger.debug('calculated command width: %s, argument width: %s' % (command_width, argument_width))
        usage = 'Available commands:'
        for command, argument, description in lines:
            usage += '\n    {}    {}    {}'.format(command.ljust(command_width), argument.ljust(argument_width), description)

        usage += '\n'
        usage += '\n    {}    {}    {}'.format('help'.ljust(command_width), ''.ljust(argument_width), self.help_description_help)
        usage += '\n    {}    {}    {}'.format('exit'.ljust(command_width), ''.ljust(argument_width), self.help_description_exit)
        usage += '\n'

        print(usage)
