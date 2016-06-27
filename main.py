import logging
import sys

from partner_tracker import setup_logging
from partner_tracker.driver import Driver
from partner_tracker.searchers import SearcherDancesportRu
from partner_tracker.cli import Mode, command

setup_logging()
logger = logging.getLogger('partner_tracker')


class ModeMain(Mode):
    @command('Load data file from disk')
    def load(self, filename: 'filename' = 'data.p'):
        driver.load(filename)

    @command('Save data file to disk')
    def save(self, filename: 'filename' = 'data.p'):
        driver.save(filename)

    @command('Search for new partners')
    def search(self, string):
        found = driver.search()
        print('Found %s new partners' % found)

    @command('Update existing partners')
    def update(self, string):
        updated, conflicts = driver.update()
        print('Updated: %s, with conflicts: %s' % (updated, conflicts))

    @command('Create new partner')
    def create(self, string):
        logger.error('create is not implemented')

    @command('Modify selected partner')
    def modify(self, partner: 'number'):
        logger.error('modify is not implemented')

    @command('List all partners with selected state')
    def list(self, string: 'state list'):
        for partner in driver.partners:
            print(partner)

    @command('Go to selected partner sub-mode')
    def open(self, index: 'number'):
        """Go to selected partner's sub-mode"""
        logger.error('open is not implemented')

    @command('Import old database format')
    def importdb(self, filename: 'filename'):
        logger.error('import is not implemented')


if __name__ == '__main__':

    driver = Driver()
    searcher = SearcherDancesportRu()
    driver.add_searcher(searcher)

    t = ModeMain()
    t()

