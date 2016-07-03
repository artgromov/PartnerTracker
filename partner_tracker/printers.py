import logging

logger = logging.getLogger(__name__)


def to_str(field):
    if field is None:
        return ''
    else:
        return str(field)


def print_list(partners, states):
    separator = '+-----+-----------------+--------------------------------+--------------------------------+--------------------------------+---------------------------+'
    title     = '| num | name            | year sm  st la club            | description                    | last note                      | state                     |'

    template = '| {:>3.3} | {:15.15} | {:4.4} {:3.3} {:2.2} {:2.2} {:15.15} | {:30.30} | {:30.30} | {:25.25} |'

    lines = [separator,
             title,
             separator
             ]

    for num, obj in enumerate(partners):
        try:
            last_note = obj.notes[-1]
        except IndexError:
            last_note = ''

        string = template.format(to_str(num + 1),
                                 to_str(obj.name),
                                 to_str(obj.birth),
                                 to_str(obj.height),
                                 to_str(obj.class_st),
                                 to_str(obj.class_la),
                                 to_str(obj.club),
                                 to_str(obj.description),
                                 to_str(last_note),
                                 to_str(obj.state)
                                 )
        lines.append(string)
    lines.append(separator)

    if len(partners) > 0:
        print('\n'.join(lines))
    else:
        print('No partners found')


def print_conflicts(partners):
    separator = '+-----+-----------------+--------------------------------+----------------------------------------------------+'
    title     = '| num | name            | field                          | values                                             |'

    template = '| {:>3.3} | {:15.15} | {:30.30} | {:50.50} |'

    lines = [separator,
             title,
             separator
             ]

    counter = 0
    for num, obj in enumerate(partners):
        if obj.conflicts:
            counter += 1
            for i, name in enumerate(obj.conflicts.keys()):
                for j, value in enumerate(obj.conflicts[name]):
                    if i == 0 and j == 0:
                        string = template.format(to_str(num + 1),
                                                 to_str(obj.name),
                                                 to_str(name),
                                                 to_str(value)
                                                 )
                    elif i != 0 and j == 0:
                        string = template.format('',
                                                 '',
                                                 to_str(name),
                                                 to_str(value)
                                                 )
                    else:
                        string = template.format('',
                                                 '',
                                                 '',
                                                 to_str(value)
                                                 )
                    lines.append(string)
            lines.append(separator)

    if counter > 0:
        print('\n'.join(lines))
    else:
        print('No conflicts found')
