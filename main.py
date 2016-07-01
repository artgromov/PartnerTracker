import logging
import sys

from partner_tracker import setup_logging
from partner_tracker.driver import Driver
from partner_tracker.searchers import SearcherDancesportRu
from partner_tracker.prints import print_list
from cli.blocks import Mode, Command

setup_logging()
logger = logging.getLogger('partner_tracker')


class MainMode(Mode):
    def __init__(self):
        self.name = 'main'
        self.context = ''

        self.driver = Driver()
        self.driver.add_searcher(SearcherDancesportRu())

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

    @Command('Create new partner')
    def create(self):
        logger.error('create is not implemented')

    @Command('Modify selected partner')
    def modify(self, number: 'Number of partner to edit from list command output'):
        """Redirects to selected partner's sub-mode for editing"""
        logger.error('modify is not implemented')

    @Command('List all partners with selected state')
    def list(self, states: 'State list to filter output. Examples: 1-5, 1,4-5. Defaults: 1-5'='1-5'):
        print_list(self.driver.partners)

    @Command('Go to selected partner sub-mode')
    def open(self, index: 'Number of partner to open from list command output'):
        """Open specified parter in system's default web browser"""
        logger.error('open is not implemented')

    @Command('Import old database format')
    def importdb(self, filename: 'File to import from'):
        logger.error('import is not implemented')


if __name__ == '__main__':
    main_mode = MainMode()
    main_mode()
