import logging
import uuid
import re
import webbrowser
from textwrap import wrap

from partner_tracker.updaters import update

logger = logging.getLogger(__name__)


class State:
    states = ['Created',
              'First time updated',
              'First contact attempt',
              'Awaiting additional info',
              'Primary testing scheduled',
              'Advanced testing',
              'Ignored',
              'No answer'
              ]

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return self.states[self.id]


class Partner:
    _schedule_pattern = re.compile('^(?P<rate>[0-9])p(?P<num>[0-9]?)(?P<interval>[wmy])')
    _schedule_intervals = {'w': 'week',
                           'm': 'month',
                           'y': 'year'
                           }

    def __init__(self):
        self.id = uuid.uuid4()
        self.state = State(0)
        self.conflicts = dict()

        self.name = None
        self.phone = None
        self.email = None

        self.country = None
        self.city = None
        self.org = None
        self.club = None
        self.trainer = None
        self.class_st = None
        self.class_la = None
        self.birth = None
        self.height = None
        self.weight = None
        self.description = None

        self.goal = None
        self.expectations = None
        self.competition_last_date = None
        self.links = []
        self.images = []
        self.videos = []

        self.change_org = None
        self.change_club = None
        self.change_trainer = None

        self.schedule_practice = None
        self.schedule_coached_practice = None
        self.schedule_competition = None
        self.schedule_training_time = None

        self.notes = []

    def __repr__(self):
        return 'Partner<{} {} {} {} {}>'.format(repr(self.state), str(self.class_st), str(self.class_la), str(self.name), str(self.description))

    def __str__(self):
        string = ''
        for key in sorted(self.__dict__.keys()):
            string += '%s: %s\n' % (key, self.__dict__[key])
        return string.rstrip()

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def update_attribute(self, name, new_value, forced=False):
        old_value = self.__dict__[name]
        updated = 0

        if old_value is None and new_value is not None:
            logger.debug('updating attribute: "%s" with value: "%s"' % (name, new_value))
            self.__dict__[name] = new_value
            updated = 1

        elif isinstance(old_value, list):
            if isinstance(new_value, list) or isinstance(new_value, tuple):
                for item in new_value:
                    if item not in old_value:
                        logger.debug('adding new item "%s" to  attribute "%s"' % (item, name))
                        self.__dict__[name].append(str(item))
                        updated = 1
            else:
                if new_value not in old_value:
                    logger.debug('adding new item "%s" to  attribute "%s"' % (new_value, name))
                    self.__dict__[name].append(str(new_value))
                    updated = 1

        elif forced:
            logger.debug('forced updating attribute: "%s" with value: "%s"' % (name, new_value))
            self.__dict__[name] = new_value
            try:
                self.conflicts.pop(name)
            except KeyError:
                pass
            updated = 1

        elif old_value != new_value:
                logger.debug('conflict found for attribute: "%s"' % name)
                if name not in self.conflicts:
                    self.conflicts[name] = [old_value]

                if new_value not in self.conflicts[name]:
                    self.conflicts[name].append(new_value)

                updated = 1

        return updated

    def update(self):
        changed = 0
        if self.links:
            for link in self.links:
                logger.debug('updating from %s' % link)
                local_counter = 0
                new_data = update(link)
                if new_data:
                    for name, new_value in new_data.items():
                        local_counter += self.update_attribute(name, new_value)

                if local_counter > 0:
                    changed = 1
                    if self.state.id == 0:
                        self.state = State(1)

        else:
            logger.debug('cannot update, no source links specified')

        return changed

    def wrap_attr(self, name):
        value = self.__dict__[name]
        lines = []

        template = '| {:30.30} | {:70.70} |'

        if value is None:
            value = ['']

        elif isinstance(value, str):
            value = wrap(value, 70)

        elif isinstance(value, list):
            if len(value) == 0:
                value = ['']

        else:
            value = wrap(str(value), 70)

        for num, item in enumerate(value):
            if num == 0:
                lines.append(template.format(name, item))
            else:
                lines.append(template.format('', item))

        return lines

    def print(self, attribute=None):
        separator = ['+--------------------------------+------------------------------------------------------------------------+']

        lines = []

        if attribute is None:
            logger.debug('printing full info')
            lines += separator
            lines += self.wrap_attr('name')
            lines += self.wrap_attr('phone')
            lines += self.wrap_attr('email')
            lines += separator
            lines += self.wrap_attr('state')
            lines += separator
            lines += self.wrap_attr('country')
            lines += self.wrap_attr('city')
            lines += self.wrap_attr('org')
            lines += self.wrap_attr('club')
            lines += self.wrap_attr('trainer')
            lines += self.wrap_attr('class_st')
            lines += self.wrap_attr('class_la')
            lines += self.wrap_attr('birth')
            lines += self.wrap_attr('height')
            lines += self.wrap_attr('weight')
            lines += self.wrap_attr('description')
            lines += separator
            lines += self.wrap_attr('links')
            lines += self.wrap_attr('images')
            lines += self.wrap_attr('videos')
            lines += separator
            lines += self.wrap_attr('goal')
            lines += self.wrap_attr('expectations')
            lines += self.wrap_attr('competition_last_date')
            lines += separator
            lines += self.wrap_attr('change_org')
            lines += self.wrap_attr('change_club')
            lines += self.wrap_attr('change_trainer')
            lines += separator
            lines += self.wrap_attr('schedule_practice')
            lines += self.wrap_attr('schedule_coached_practice')
            lines += self.wrap_attr('schedule_competition')
            lines += self.wrap_attr('schedule_training_time')
            lines += separator
            lines += self.wrap_attr('conflicts')
            lines += separator
            lines += self.wrap_attr('notes')
            lines += separator

            print('\n'.join(lines))

        else:
            logger.debug('printing attribute "%s"' % attribute)
            lines += separator
            lines += self.wrap_attr(attribute)
            lines += separator

            print('\n'.join(lines))

    def browse(self):
        if len(self.links) > 0:
            for link in self.links:
                logger.debug('opening link %s in web browser' % link)
                webbrowser.open(link)
        else:
            logger.error('no links found')
            raise NoLinksFound


class MyException(Exception):
    def __init__(self, msg):
        self.msg = msg

class NoLinksFound(MyException):
    pass
