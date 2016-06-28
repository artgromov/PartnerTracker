import logging

logger = logging.getLogger(__name__)


class Command:
    """
    Commandlet fabric class. Use as decorator for Mode methods.
    """

    number_free = 0
    number_used = set()

    def __init__(self, description='', command=None, number=None):
        self.description = description
        self.command = command
        self.number = self.set_number(number)

    def __call__(self, func):
        description = self.description
        command = self.get_command(func)
        number = self.number

        new_commandlet = Commandlet(description, command, number, func)
        return new_commandlet

    @classmethod
    def set_number(cls, number):
        if number is None:
            num = cls.number_free
            cls.number_free += 1
        else:
            num = int(number)

        while True:
            if num in cls.number_used:
                num += 1
            else:
                break
        return num

    def get_command(self, func):
        if self.command is None:
            return func.__name__
        else:
            return self.command


class Commandlet:
    command_width = 0
    arguments_width = 0

    def __init__(self, description, command, number, func):
        self.description = description
        self.command = command
        self.number = number
        self.func = func
        self.func_help = func.__doc__

        arguments = []
        for num, arg in enumerate(func.__code__.co_varnames):
            if arg != 'self' and num < func.__code__.co_argcount:
                arguments.append(arg)

        self.arguments = tuple(arguments)
        self.arguments_string = ' '.join(['[%s]' % arg for arg in arguments])
        self.arguments_help = func.__annotations__

        arguments_width = len(self.arguments_string)
        if Commandlet.arguments_width < arguments_width:
            Commandlet.arguments_width = arguments_width

        command_width = len(command)
        if Commandlet.command_width < command_width:
            Commandlet.command_width = command_width

    @property
    def short_help(self):
        return '\t%s    %s    %s' % (self.command.ljust(self.command_width), self.arguments_string.ljust(self.arguments_width), self.description)

    @property
    def long_help(self):
        lines = []
        lines.append('Name:')
        if self.description:
            lines.append('\t%s - %s' % (self.command, self.description))
        else:
            lines.append(self.command)
        lines.append('')
        lines.append('Usage:')
        lines.append('\t%s %s' % (self.command, self.arguments_string))

        if self.arguments_help:
            lines.append('')
            lines.append('Arguments:')

            arg_width = 0
            arg_lines = []
            for arg_name in self.arguments:
                try:
                    arg_help = self.arguments_help[arg_name]
                except KeyError:
                    continue
                else:
                    if arg_width < len(arg_name):
                        arg_width = len(arg_name)
                    arg_lines.append((arg_name, arg_help))

            for arg in arg_lines:
                lines.append('\t%s - %s' % (arg[0].ljust(arg_width), arg[1]))

        if self.func_help:
            lines.append('')
            lines.append('Description:')
            func_help_lines = [i.strip() for i in self.func_help.strip().split('\n')]
            lines.append('\t' + '\n\t'.join(func_help_lines))

        return '\n'.join(lines)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return 'Command(%s)' % self.command

    def __hash__(self):
        return hash(self.command)

    def __eq__(self, other):
        return self.command == other.command


class Mode:
    def __call__(self):
        self.build_namespace()

        while True:
            command_input, argument_input = self.get_user_input()
            try:
                command = self.lookup_command(command_input)
                if argument_input:
                    logger.debug('calling %s(%s)' % (command.command, argument_input))
                    command(self, argument_input)
                else:
                    logger.debug('calling %s()' % command.command)
                    command(self)

            except KeyError:
                print('Unknown command %s' % command_input)
            except StopIteration:
                break

    def __repr__(self):
        name = self.__dict__.get('name', 'default_name')
        context = self.__dict__.get('context', '<default_context>')
        return '<Mode name=%s, context=%s>' % (name, context)

    def build_namespace(self):
        namespace = []

        def get_commandlets(cls):
            for key, value in cls.__dict__.items():
                if isinstance(value, Commandlet):
                    if value not in namespace:
                        namespace.append(value)
            for base in cls.__bases__:
                get_commandlets(base)

        get_commandlets(self.__class__)
        self.namespace = namespace

    def get_user_input(self):
        name = self.__dict__.get('name', 'default_name')
        context = self.__dict__.get('context', '<default_context>')
        prompt = '%s%s: ' % (name, context)
        user_input = input(prompt).strip()
        command_input = user_input.split(' ')[0]
        argument_input = ' '.join(user_input.split(' ')[1:])
        return command_input, argument_input

    def lookup_command(self, command_input):
        for command in self.namespace:
            if command.command == command_input:
                return command
        raise KeyError

    @Command('Print this message', number=998)
    def help(self, command_name: 'Specifies command name to get detailed usage information.'=''):
        """
        Prints list of available commands of current mode, or detailed command info if command name is specified.
        """

        if not command_name:
            logger.debug('printing basic help')
            print('Available commands:')
            for command in sorted(self.namespace, key=lambda x: x.number):
                print(command.short_help)
            print()

        else:
            logger.debug('printing detailed help for %s' % command_name)
            try:
                command = self.lookup_command(command_name)
            except KeyError:
                print('Unknown command %s' % command_name)
            else:
                print(command.long_help)
            print()

    @Command(number='999')
    def exit(self):
        raise StopIteration
