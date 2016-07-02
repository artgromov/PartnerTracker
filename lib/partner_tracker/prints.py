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
    print('\n'.join(lines))


def print_conflicts(partners):
    separator = '+-------+'
    title     = '| bla   |'

    template  = ''
    template_filler = ''

    lines = [separator,
             title,
             separator
             ]

    for num, obj in enumerate(partners):
        if obj.conflicts:
            string = ''
            lines.append(string)
    print('\n'.join(lines))


def print_info(partner):
    print(partner)




'''
state
providers
conflicts

name
phone
email

country
city
org
club
trainer
class_st
class_la
birth
height
description

goal
expectations
competition_last_date
image
video

change_org
change_club
change_trainer

schedule_practice
schedule_coached_practice
schedule_competition
schedule_training_time

notes
'''
