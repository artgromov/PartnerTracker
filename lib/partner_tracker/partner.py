import logging
import uuid
import re

logger = logging.getLogger(__name__)


class Partner:
    NEW = 'Created'
    UPD = 'First time updated'
    ACK = 'First contact attempt'
    WAIT = 'Awaiting additional info'
    PTEST = 'Primary testing scheduled'
    ATEST = 'Advanced testing'
    IGN = 'Ignored'
    NOAN = 'Still no answer'
    NA = 'Source not found'
    DEL = 'Should be deleted'

    _schedule_pattern = re.compile('^(?P<rate>[0-9])p(?P<num>[0-9]?)(?P<interval>[wmy])')
    _schedule_intervals = {'w': 'week',
                           'm': 'month',
                           'y': 'year'
                           }

    def __init__(self):
        self.id = uuid.uuid4()
        self.state = Partner.NEW
        self.providers = set()
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
        self.images = set()
        self.videos = set()

        self.change_org = None
        self.change_club = None
        self.change_trainer = None

        self.schedule_practice = None
        self.schedule_coached_practice = None
        self.schedule_competition = None
        self.schedule_training_time = None

        self.notes = []

    def __repr__(self):
        return 'Partner<{state:25} {name:20} {class_st:1} {class_la:1} {description:27.27}>'.format(**self.__dict__)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def add_provider(self, provider):
        logger.debug('attaching new provider: "%s"' % provider.id)
        self.providers.add(provider)

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

                elif isinstance(old_value, set):
                    logger.debug('updating attribute: "%s" with value: "%s"' % (name, new_value))
                    self.__dict__[name].update(set(new_value))
                    return 1

                elif old_value != new_value:
                    logger.debug('conflict found for attribute: "%s"' % name)
                    if name not in self.conflicts:
                        self.conflicts[name] = set(old_value)
                    self.conflicts[name].add(new_value)
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
        return changed


