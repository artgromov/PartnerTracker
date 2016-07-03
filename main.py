import logging
from datetime import datetime

from partner_tracker import setup_logging
from partner_tracker.driver import Driver
from partner_tracker.partner import Partner, State, NoLinksFound
from partner_tracker.printers import print_list, print_conflicts
from cli.blocks import Mode, Command, IncorrectArguments

setup_logging()
logger = logging.getLogger('partner_tracker')


class MainMode(Mode):
    def __init__(self):
        self.name = 'main'
        self.context = ''

        self.driver = Driver()

    def get_partner(self, number):
        index = get_index(number, len(self.driver.partners))
        partner = self.driver.partners[index]
        return number, partner

    @Command('Load data from disk')
    def load(self, filename: 'File name to load from disk' = 'data.p'):
        try:
            self.driver.load(filename)
            print('Data is loaded from file %s' % filename)
        except FileNotFoundError:
            print('File "%s" not found' % filename)

    @Command('Save data to disk')
    def save(self, filename: 'File name to save to disk' = 'data.p'):
        self.driver.save(filename)
        print('Data is saved to file %s' % filename)

    @Command('List all partners with selected state')
    def list(self, states: 'State list to filter output. Examples: 1-5, 1,4-5. Defaults: 1-5'='1-5'):
        print_list(self.driver.partners, states)

    @Command('Print detailed info for partner with selected number')
    def show(self, number: 'Print detailed info for partner with selected nubmer', attribute: 'Defines attribute name to show'=None):
        number, partner = self.get_partner(number)
        try:
            partner.print(attribute)
        except KeyError:
            raise IncorrectArguments('no such attribute %s' % attribute)

    @Command('Open in web browser')
    def open(self, number: 'Open web advertisement of partner with selected number'):
        """Open specified parter's dancesport.ru advertisment in system's default web browser"""
        number, partner = self.get_partner(number)
        try:
            partner.browse()
        except NoLinksFound:
            print('No links found')

    @Command('Edit selected partner"s attributes')
    def edit(self, number: 'Number of partner to edit from list command output'):
        """Redirects to selected partner's sub-mode for editing"""
        number, partner = self.get_partner(number)
        partner_mode = PartnerMode(number, partner)
        partner_mode()

    @Command('Search for new partners')
    def search(self):
        found = self.driver.search()
        print('Found %s new partners' % found)

    @Command('Update existing partners')
    def update(self):
        updated, conflicts = self.driver.update()
        print('Updated: %s, with conflicts: %s' % (updated, conflicts))

    @Command('Create new partner')
    def create(self):
        index = len(self.driver.partners)
        number = index + 1
        logger.debug('new partner index: %s, number: %s' % (number, index))
        partner = Partner()
        self.driver.partners.append(partner)
        partner_mode = PartnerMode(number, partner)
        partner_mode()

    @Command('Delete selected partner')
    def delete(self, number: 'Number of partner to delete'):
        index = get_index(number, len(self.driver.partners))
        while True:
            key = input('You are going to delete partner number: %s, name: %s. Is it correct (y/n) [n]? ' % (number, self.driver.partners[index].name))
            if key == '' or key in 'Nn':
                print('Operation cancelled')
                break

            elif key in 'Yy':
                self.driver.partners.pop(index)
                print('Deleted successfully')
                break

    @Command('List all partners with merged conflicts')
    def conflicts(self):
        print_conflicts(self.driver.partners)

    @Command('Import old database format')
    def importdb(self, filename: 'File to import from'):
        import yaml

        states = {'init': 1,
                  'syn': 2,
                  'ack': 3,
                  'full': 4,
                  'test': 5,
                  'ignore': 6,
                  'na': 7,
                  'noan': 7,
                  }

        with open(filename) as file:
            data = yaml.load(file.read())
            for partner in self.driver.partners:
                for item in data:
                    if partner.links[0] == item['link']:
                        partner.update_attribute('notes', item['notes'])
                        partner.state.id = states[item['state']]


class PartnerMode(Mode):
    def __init__(self, number, partner):
        self.name = 'main/partner'
        self.context = str(number)
        self.partner = partner

    @Command('Print detailed info')
    def show(self, attribute: 'Defines attribute name to show'=None):
        try:
            self.partner.print(attribute)
        except KeyError:
            raise IncorrectArguments('no such attribute %s' % attribute)

    @Command('Open in web browser')
    def open(self):
        try:
            self.partner.browse()
        except NoLinksFound:
            print('No links found')

    @Command('Set attribute to new value')
    def set(self, attribute: 'Defines attribute name', value: 'New value for attribute'=''):
        read_only = ('id', 'conflicts', 'notes', 'state')
        if attribute in read_only:
            raise IncorrectArguments('attribute cannot be modified with this command')

        elif attribute in self.partner.__dict__:
            if attribute not in self.partner.conflicts:
                self.partner.update_attribute(attribute, value, forced=True)

            else:
                self.partner.update_attribute(attribute, value)
                values = self.partner.conflicts[attribute]
                print('Conflicted values for %s:' % attribute)
                for num, line in enumerate(values):
                    print('\t{}. {}'.format(num + 1, line))
                print()
                default = len(values) - 1
                while True:
                    key = input('Choose which value to write [%s]: ' % (default + 1))
                    if key == '':
                        value = values[default]
                        logger.debug('using default value: %s' % value)
                        self.partner.update_attribute(attribute, value, forced=True)
                        break

                    else:
                        try:
                            index = int(key) - 1
                        except ValueError:
                            print('Incorrect symbol, must be digit.')
                        else:
                            try:
                                value = values[index]
                            except IndexError:
                                print('Incorrect value, must be between 1 and %s.' % (default + 1))
                            else:
                                logger.debug('using value: %s' % value)
                                self.partner.update_attribute(attribute, value, forced=True)
                                break

        else:
            raise IncorrectArguments('no such attribute')

    @Command('Reset attribute conflicts, removes all conflicts if no attribute specified')
    def reset(self, attribute: 'Attribute name'=None):
        if attribute is None:
            self.partner.conflicts = dict()
            print('All conflicts removed' % attribute)

        else:
            try:
                self.partner.conflicts.pop(attribute)
            except KeyError:
                if attribute in self.partner.__dict__:
                    raise IncorrectArguments('no conflicts found for attribute %s' % attribute)
                else:
                    raise IncorrectArguments('no such attribute')
            else:
                print('Conflicts for attribute %s removed' % attribute)

    @Command('Show or change partner state')
    def state(self, state: 'Specify number to change state. If empty, shows available states'=''):
        states = State.states
        if state == '':
            print('Current state: %s' % self.partner.state)
            print('Available states:')
            for n, line in enumerate(states):
                print('\t{}. {}'.format(n+1, line))
            print()

        else:
            index = get_index(state, len(states))
            logger.debug('udpating partner state from %s to %s' % (self.partner.state.id, index))
            self.partner.state.id = index
            print('State changed to %s' % self.partner.state)

    @Command('Add or remove notes')
    def notes(self, action: 'Specify <add|del>'='', data: 'Text field when action=add, number to delete when action=del'=''):
        notes = self.partner.notes
        if action == 'add':
            if data == '':
                raise IncorrectArguments('new note data is empty')
            else:
                timestamp = datetime.now().strftime('%Y-%m-%d')
                notes.append('{} {}'.format(timestamp, data))

        elif action == 'del':
            if data.isdigit():
                number = (int(data) - 1)
                if number in list(range(len(notes))):
                    notes.pop(number)
                else:
                    raise IncorrectArguments('incorrect note number')
            else:
                raise IncorrectArguments('incorrect note number')

        elif action == '':
            if len(notes) > 0:
                print('Notes:')
                for n, line in enumerate(notes):
                    print('\t{}. {}'.format(n+1, line))
                print()
            else:
                print('No notes found')

        else:
            raise IncorrectArguments('incorrect action for note command')

    @Command('Update current partner')
    def update(self):
        if len(self.partner.links) > 0:
            if self.partner.update():
                if self.partner.conflicts:
                    print('Updated with conflicts')
                else:
                    print('Updated successfully')
            else:
                print('No updates found')
        else:
            print('No source links found')


def get_index(string, max_value, min_value=0):
    if string.isdigit():
        index = int(string) - 1
    else:
        raise IncorrectArguments('"%s" incorrect symbol' % string)

    if index in list(range(min_value, max_value)):
        return index
    else:
        raise IncorrectArguments('"%s" is not within correct number range' % string)


if __name__ == '__main__':
    try:
        main_mode = MainMode()
        main_mode()
    except KeyboardInterrupt:
        print('Exiting...')
