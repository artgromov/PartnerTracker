import logging
import uuid
import sys
import re


class Partner:
    NEW     = 'Created'
    UPD     = 'First time updated'
    ACK     = 'First contact attempt'
    WAIT    = 'Awaiting additional info'
    PTEST   = 'Primary testing scheduled'
    ATEST   = 'Advanced testing'
    IGN     = 'Ignored'
    NOAN    = 'Still no answer'
    NA      = 'Source not found'

    _schedule_pattern = re.compile('^(?P<rate>[0-9])p(?P<num>[0-9]?)(?P<interval>[wmy])')
    _schedule_intervals = {'w': 'week',
                           'm': 'month',
                           'y': 'year'
                           }


    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.id = uuid.uuid4()
        self.state = Partner.NEW

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
        self.links = []

        self.change_org = None
        self.change_club = None
        self.change_trainer = None

        self.schedule_practice = None
        self.schedule_coached_practice = None
        self.schedule_competition = None
        self.schedule_training_time = None

        self.notes = []
        
        self.provider = None

    def __repr__(self):
        return '<{state:25} {name:20} {class_st:1} {class_la:1} {description:27.27}>'.format(**self.__dict__)


    def set_schedule(self, spec):
        match = _schedule_pattern.search(spec)
        changed = False
        if match:
            rate = match.group('rate')
            num = match.group('num')
            interval = self._schedule_intervals[match.group('interval')]

            if num:
                if int(num) > 1:
                    interval = interval + 's'
                schedule = '{} per {} {}'.format(rate, num, interval)

            else:
                schedule = '{} per {}'.format(rate, interval)

            self.log.debug('schedule set to "{}"'.format(schedule))
            changed = True

        else:
            self.log.error('incorrect schedule specification "{}"'.format(spec))
        
        return changed

    def diff(self, other):
        diff = {}
        for key in self.__dict__.keys():
            if key != log:
                self_attr = self.__dict__[key]
                other_attr = other.__dict__[key]
                if self_attr != other_attr:
                    diff[key] = (self_attr, other_attr)

        return diff

    def merge_dict(self, data):
        changed = False
        for key in self.__dict__.keys():
            try:
                if self.__dict__[key] != data[key]:
                    self.data[key] = data[key]
                    changed = True
            except KeyError:
                pass

        return changed



if __name__ == '__main__':
    a = Partner()
    print(a.__dict__)
