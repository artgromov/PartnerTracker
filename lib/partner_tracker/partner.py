import logging
import uuid
import re

logger = logging.getLogger(__name__)


class State:
    states = [('S_NEW', 'Created'),
              ('S_UPD', 'First time updated'),
              ('S_ACK', 'First contact attempt'),
              ('S_WAIT', 'Awaiting additional info'),
              ('S_PTEST', 'Primary testing scheduled'),
              ('S_ATEST', 'Advanced testing'),
              ('S_IGN', 'Ignored'),
              ('S_NOAN', 'No answer')
              ]

    state_set = set([i[0] for i in states])
    state_dict = {k: v for k, v in states}

    def __init__(self, state):
        if state in self.state_set:
            self.state = state
        else:
            raise KeyError

    def __repr__(self):
        return 'State(%s)' % self.state

    def __str__(self):
        return self.state_dict[self.state]

S_NEW = State('S_NEW')
S_UPD = State('S_UPD')
S_ACK = State('S_ACK')
S_WAIT = State('S_WAIT')
S_PTEST = State('S_PTEST')
S_ATEST = State('S_ATEST')
S_IGN = State('S_IGN')
S_NOAN = State('S_NOAN')


class Partner:
    _schedule_pattern = re.compile('^(?P<rate>[0-9])p(?P<num>[0-9]?)(?P<interval>[wmy])')
    _schedule_intervals = {'w': 'week',
                           'm': 'month',
                           'y': 'year'
                           }

    def __init__(self):
        self.id = uuid.uuid4()
        self.state = S_NEW
        self.providers = []
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
        self.description = None

        self.goal = None
        self.expectations = None
        self.competition_last_date = None
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

    def add_provider(self, provider):
        if provider not in self.providers:
            logger.debug('attaching new provider: "%s"' % provider.id)
            self.providers.append(provider)

    def update_attribute(self, name, new_value, forced=False):
        if new_value:
            old_value = self.__dict__[name]

            if old_value == new_value:
                return 0

            if not forced:
                if not old_value:
                    logger.debug('updating attribute: "%s" with value: "%s"' % (name, new_value))
                    self.__dict__[name] = new_value
                    return 1

                elif isinstance(old_value, list):
                    logger.debug('updating attribute: "%s" with value: "%s"' % (name, new_value))
                    self.__dict__[name] = list(set(old_value + new_value))
                    return 1

                elif old_value != new_value:
                    logger.debug('conflict found for attribute: "%s"' % name)
                    if name not in self.conflicts:
                        self.conflicts[name] = [old_value]

                    if new_value not in self.conflicts[name]:
                        self.conflicts[name].append(new_value)

                    return 0

            else:
                logger.debug('forced updating attribute: "%s" with value: "%s"' % (name, new_value))
                self.__dict__[name] = new_value
                return 1

    def update(self):
        changed = 0
        for provider in self.providers:
            local_counter = 0
            provider.update()
            new_data = provider.get_changes()
            if new_data:
                for name, new_value in new_data.items():
                    local_counter += self.update_attribute(name, new_value)

                provider.reset_changes()

            if local_counter > 0:
                changed = 1
                if self.state == S_NEW:
                    self.state = S_UPD

        return changed
