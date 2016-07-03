import logging
import uuid
import re

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

    def __init__(self, state_num):
        self.state = state_num

    def __repr__(self):
        return self.states[self.state]

NEW = State(0)
UPD = State(1)
ACK = State(2)
WAIT = State(3)
PTEST = State(4)
ATEST = State(5)
IGN = State(6)
NOAN = State(7)


class Partner:
    _schedule_pattern = re.compile('^(?P<rate>[0-9])p(?P<num>[0-9]?)(?P<interval>[wmy])')
    _schedule_intervals = {'w': 'week',
                           'm': 'month',
                           'y': 'year'
                           }

    def __init__(self):
        self.id = uuid.uuid4()
        self.state = NEW
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

        if old_value == new_value:
            return 0

        elif old_value is None:
            logger.debug('updating attribute: "%s" with value: "%s"' % (name, new_value))
            self.__dict__[name] = new_value
            return 1

        elif isinstance(old_value, list):
            if new_value not in old_value:
                logger.debug('updating attribute: "%s" with value: "%s"' % (name, new_value))
                if isinstance(new_value, list) or isinstance(new_value, tuple):
                    self.__dict__[name] += list(new_value)
                else:
                    self.__dict__[name].append(new_value)
                return 1
            else:
                return 0

        elif old_value != new_value:
            if not forced:
                logger.debug('conflict found for attribute: "%s"' % name)
                if name not in self.conflicts:
                    self.conflicts[name] = [old_value]

                if new_value not in self.conflicts[name]:
                    self.conflicts[name].append(new_value)

                return 1

            else:
                logger.debug('forced updating attribute: "%s" with value: "%s"' % (name, new_value))
                self.__dict__[name] = new_value
                try:
                    self.conflicts.pop(name)
                except KeyError:
                    pass

                return 1

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
                    if self.state == NEW:
                        self.state = UPD

        else:
            logger.debug('cannot update, no source links specified')

        return changed



