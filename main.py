import logging
import sys

from partner_tracker import setup_logging
from partner_tracker.driver import Driver
from partner_tracker.searchers import SearcherDancesportRu
from partner_tracker.cli import Mode

setup_logging()
logger = logging.getLogger('partner_tracker')


def callback_load(filename: 'filename' = 'data.p'):
    """Load data file from disk"""
    driver.load(filename)


def callback_save(filename: 'filename' = 'data.p'):
    """Save data file to disk"""
    driver.save(filename)


def callback_search(string):
    """Search for new partners"""
    found = driver.search()
    print('Found %s new partners' % found)


def callback_update(string):
    """Update existing partners"""
    updated, conflicts = driver.update()
    print('Updated: %s, with conflicts: %s' % (updated, conflicts))


def callback_create(string):
    """Create new partner"""
    logger.error('create is not implemented')


def callback_modify(partner: 'number'):
    """Modify selected partner"""
    logger.error('modify is not implemented')


def callback_list(string: 'state list'):
    """List all partners with selected state"""
    for partner in driver.partners:
        print(partner)


def callback_open(index: 'number'):
    """Go to selected partner's sub-mode"""
    logger.error('open is not implemented')
    mode_partner = Mode('main/partner(%s): ' % index)

    try:
        partner = driver.partners[index]
    except TypeError:
        logger.error('wrong argument: %s' % partner)
    except IndexError:
        logger.error('wrong partner number: %s' % partner)
    else:
        mode_partner.partner = partner


def callback_import(filename: 'filename'):
    """Import old database format"""
    logger.error('import is not implemented')


def callback_partner_modify(partner, attr_name, value):
    """Modify attribute"""
    logger.error('not implemented')


if __name__ == '__main__':

    driver = Driver()
    searcher = SearcherDancesportRu()
    driver.add_searcher(searcher)

    mode_main = Mode('main: ', root=True)
    mode_main.add_command('load', callback_load)
    mode_main.add_command('save', callback_save)
    mode_main.add_command('search', callback_search)
    mode_main.add_command('update', callback_update)
    mode_main.add_command('create', callback_create)
    mode_main.add_command('modify', callback_modify)
    mode_main.add_command('list', callback_list)
    mode_main.add_command('open', callback_open)
    mode_main.add_command('import', callback_import)

    mode_main()

    sys.exit(0)
