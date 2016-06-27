import logging

logger = logging.getLogger(__name__)


def command(description=None, command=None, arghelp=None, fullhelp=None, number=None):
    def decorate(func):
        new_command = Command(description, command, arghelp, fullhelp, number, func)
        return new_command
    return decorate


class Command:
    number = 0
    number_used = set()

    def __new__(cls, description, command, arghelp, fullhelp, number, func):
        instance = super().__new__(cls)
        if number is None:
            num = cls.number
            cls.number += 1
        else:
            num = int(number)

        while True:
            if num in cls.number_used:
                num += 1
            else:
                break

        instance.number = num
        cls.number_used.add(num)
        return instance

    def __init__(self, description, command, arghelp, fullhelp, number, func):
        self.description = description
        self.command = command
        self.arghelp = arghelp
        self.fullhelp = description
        self.func = func

        if not command:
            self.command = func.__name__

        if not arghelp:
            self.arghelp = 'add from annotations'

        if not fullhelp:
            self.fullhelp = func.__doc__

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return 'Command(%s)' % self.command


class Mode:
    def __call__(self):
        self.namespace = []
        self.build_namespace(self.__class__)

        while True:
            command_input, argument_input = self.get_user_input()
            try:
                command = self.lookup_command(command_input)
                logger.debug('calling %s(%s)' % (command.command, argument_input))
                command(self, argument_input)
            except KeyError:
                print('Unknown command %s' % command_input)
            except StopIteration:
                break

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, self.name)

    def __str__(self):
        return type(self).__name__

    def build_namespace(self, cls):
        for key, value in cls.__dict__.items():
            if isinstance(value, Command):
                self.namespace.append(value)

        for base in cls.__bases__:
            self.build_namespace(base)

    def get_user_input(self):
        prompt = '%s%s: ' % (self.__dict__.get('name', 'default_name'), self.__dict__.get('context', '<default_context>'))
        user_input = input(prompt).strip()
        command = user_input.split(' ')[0]
        argument = ' '.join(user_input.split(' ')[1:])
        return command, argument

    def lookup_command(self, command_input):
        for command in self.namespace:
            if command.command == command_input:
                return command
        raise KeyError

    @command('Print this message', number=998)
    def help(self, argument_input):
        for i in sorted(self.namespace, key=lambda x: x.number):
            print(i.number, i.command)

    @command(number='999')
    def exit(self, argument_input):
        raise StopIteration
