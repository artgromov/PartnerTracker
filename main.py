import logging
import webbrowser

from partner_tracker import setup_logging
from partner_tracker.driver import Driver
from partner_tracker.searchers import SearcherDancesportRu
from partner_tracker.providers import ProviderDancesportRu
from partner_tracker.prints import print_list, print_info, print_attribute, print_conflicts
from cli.blocks import Mode, Command, IncorrectArguments

setup_logging()
logger = logging.getLogger('partner_tracker')


class MainMode(Mode):
    def __init__(self):
        self.name = 'main'
        self.context = ''

        self.driver = Driver()
        self.driver.add_searcher(SearcherDancesportRu())

    def get_partner(self, number):
        try:
            index = int(number) - 1
        except ValueError:
            raise IncorrectArguments('incorrect symbol passed')
        else:
            try:
                partner = self.driver.partners[index]
            except IndexError:
                raise IncorrectArguments('no partner with specified number: %s' % number)
            else:
                return partner

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
        partner = self.get_partner(number)
        print_info(partner)

    @Command('Open in web browser')
    def open(self, number: 'Open web advertisement of partner with selected number'):
        """Open specified parter's dancesport.ru advertisment in system's default web browser"""
        partner = self.get_partner(number)
        browse(partner)

    @Command('Modify selected partner')
    def modify(self, number: 'Number of partner to edit from list command output'):
        """Redirects to selected partner's sub-mode for editing"""
        partner = self.get_partner(number)
        partner_mode = PartnerMode(number, partner)
        partner_mode()

    @Command('Create new partner')
    def create(self):
        logger.error('create is not implemented')

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
    def edit(self, attribute: 'Defines attribute name to edit'):
        logger.error('edit is not implemented')

    @Command('Open in web browser')
    def open(self):
        browse(self.partner)


def browse(partner):
    if len(partner.providers) > 0:
        for provider in partner.providers:
            if isinstance(provider, ProviderDancesportRu):
                logger.debug('opening partner in web browser')
                webbrowser.open(provider.id)
            else:
                print('no dancesport.ru links found')
    else:
        print('no links found')


if __name__ == '__main__':
    main_mode = MainMode()
    main_mode()
