import logging
import webbrowser
from datetime import datetime

from partner_tracker import setup_logging
from partner_tracker.driver import Driver
from partner_tracker.partner import Partner
from partner_tracker.printers import print_list, print_info, print_attribute, print_conflicts
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
        except FileNotFoundError:
            print('File "%s" not found' % filename)

    @Command('Save data to disk')
    def save(self, filename: 'File name to save to disk' = 'data.p'):
        self.driver.save(filename)

    @Command('Search for new partners')
    def search(self):
        found = self.driver.search()
        print('Found %s new partners' % found)

    @Command('Update existing partners')
    def update(self):
        updated, conflicts = self.driver.update()
        print('Updated: %s, with conflicts: %s' % (updated, conflicts))

    @Command('List all partners with merged conflicts')
    def conflicts(self):
        print_conflicts(self.driver.partners)

    @Command('List all partners with selected state')
    def list(self, states: 'State list to filter output. Examples: 1-5, 1,4-5. Defaults: 1-5'='1-5'):
        print_list(self.driver.partners, states)

    @Command('Print detailed info for partner with selected number')
    def show(self, number: 'Print detailed info for partner with selected nubmer'):
        number, partner = self.get_partner(number)
        print_info(partner)

    @Command('Open in web browser')
    def open(self, number: 'Open web advertisement of partner with selected number'):
        """Open specified parter's dancesport.ru advertisment in system's default web browser"""
        number, partner = self.get_partner(number)
        browse(partner)

    @Command('Modify selected partner')
    def modify(self, number: 'Number of partner to edit from list command output'):
        """Redirects to selected partner's sub-mode for editing"""
        number, partner = self.get_partner(number)
        partner_mode = PartnerMode(number, partner)
        partner_mode()

    @Command('Create new partner')
    def create(self):
        number = len(self.driver.partners)
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

    @Command('Import old database format')
    def importdb(self, filename: 'File to import from'):
        logger.error('import is not implemented')


class PartnerMode(Mode):
    def __init__(self, number, partner):
        self.name = 'main/partner'
        self.context = str(number)
        self.partner = partner

    @Command('Print detailed info')
    def show(self, attribute: 'Defines attribute name to show'=None):
        if attribute is None:
            print_info(self.partner)
        else:
            try:
                print_attribute(self.partner, attribute)
            except KeyError:
                raise IncorrectArguments('no such attribute %s' % attribute)

    @Command('Edit attribute')
    def edit(self, attribute: 'Defines attribute name to edit', value: 'Set new value for attribute'):
        read_only = ('id', 'providers', 'conflicts', 'notes')
        if attribute in read_only:
            raise IncorrectArguments('attribute cannot be modified with this command')

        elif attribute in self.partner.__dict__:
            if attribute not in self.partner.conflicts:
                self.partner.update_attribute(attribute, value, forced=True)

            else:
                self.partner.update_attribute(attribute, value)
                values = self.partner.conflicts[attribute]
                num_of_values = len(values)
                print('%s conflicted values found for %s:' % (attribute, num_of_values))

                for num, line in enumerate(values):
                    print('\t{}. {}'.format(num + 1, line))

                print()
                choices = range(num_of_values)
                default_choice = num_of_values - 1
                while True:
                    index = input('Choose which value to write [%s]: ' % (default_choice + 1))
                    if index.strip() == '':
                        index = default_choice
                        logger.debug('using default value: %s' % values[index])
                        self.partner.update_attribute(attribute, values[index], forced=True)
                        break

                    elif index.isdigit():
                        index = int(index) - 1
                        if index in choices:
                            logger.debug('using value: %s' % values[index])
                            self.partner.update_attribute(attribute, values[index], forced=True)
                        break

                    else:
                        print('Incorrect value.')

        else:
            raise IncorrectArguments('no such attribute')

    @Command('Add or remove notes')
    def note(self, action: 'Specify <add|del|show>', data: 'Text field when action=add, number to delete when action=del, ignored when action=show'=''):
        notes = self.partner.notes
        if action == 'add':
            if data == '':
                raise IncorrectArguments('new note data is empty')
            else:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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

        elif action == 'show':
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

    @Command('Open in web browser')
    def open(self):
        browse(self.partner)


def get_index(string, max_value, min_value=0):
    if string.isdigit():
        index = int(string) - 1
    else:
        raise IncorrectArguments('"%s" incorrect symbol' % string)

    if index in list(range(min_value, max_value)):
        return index
    else:
        raise IncorrectArguments('"%s" is not within correct number range' % string)


def browse(partner):
    if len(partner.links) > 0:
        for link in partner.links:
            logger.debug('opening partner in web browser')
            webbrowser.open(link)
    else:
        print('No links found')


if __name__ == '__main__':
    main_mode = MainMode()
    main_mode()
