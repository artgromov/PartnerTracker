import logging

logger = logging.getLogger(__name__)


def to_str(field):
    if field is None:
        return '-'
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
                        string = template.format(to_str(num),
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


def print_info(partner):
    separator = '+--------------------------------+------------------------------------------------------------------------+'

    template = '| {:30.30} | {:70.70} |'

    def add_string(field):
        return template.format(field, to_str(partner.__dict__[field]))

    def add_list(field):
        local_lines = []
        values = partner.__dict__[field]
        if len(values) == 0:
            local_lines.append(template.format(field, ''))
            return local_lines

        else:
            for n, i in enumerate(values):
                if n == 0:
                    local_lines.append(template.format(field, to_str(i)))
                else:
                    local_lines.append(template.format('', to_str(i)))

            return local_lines

    lines = [separator,
             add_string('name'),
             add_string('phone'),
             add_string('email'),
             separator,
             add_string('state'),
             separator,
             add_string('country'),
             add_string('city'),
             add_string('org'),
             add_string('club'),
             add_string('trainer'),
             add_string('class_st'),
             add_string('class_la'),
             add_string('birth'),
             add_string('height'),
             add_string('weight'),
             add_string('description'),
             separator
             ]

    lines += add_list('links')
    lines += add_list('images')
    lines += add_list('videos')

    lines += [separator,
              add_string('goal'),
              add_string('expectations'),
              add_string('competition_last_date'),
              separator,
              add_string('change_org'),
              add_string('change_club'),
              add_string('change_trainer'),
              separator,
              add_string('schedule_practice'),
              add_string('schedule_coached_practice'),
              add_string('schedule_competition'),
              add_string('schedule_training_time'),
              ]

    lines += [separator,
              add_string('conflicts'),
              separator
              ]

    lines += add_list('notes')

    lines += [separator]

    print('\n'.join(lines))


def print_attribute(partner, attribute):
    separator = '+--------------------------------+------------------------------------------------------------------------+'

    template = '| {:30.30} | {:70.70} |'

    lines = [separator]

    value = partner.__dict__[attribute]
    if isinstance(value, list):
        if len(value) == 0:
            lines += [template.format(attribute, '')]
        else:
            for num, line in enumerate(value):
                if num == 0:
                    lines += [template.format(attribute, to_str(line))]
                else:
                    lines += [template.format('', to_str(line))]
    else:
        lines += [template.format(attribute, to_str(value))]

    lines += [separator]

    print('\n'.join(lines))
