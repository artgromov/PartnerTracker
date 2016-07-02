import logging
import pickle

from partner_tracker.searchers import search
from partner_tracker.partner import Partner

logger = logging.getLogger(__name__)


class Driver:
    def __init__(self):
        self.searchers = []
        self.links = []
        self.partners = []

    def save(self, filename):
        logger.info('saving state to file "%s"' % filename)
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    def load(self, filename):
        logger.info('loading state from file "%s"' % filename)
        with open(filename, 'rb') as file:
            loaded_obj = pickle.load(file)
        self.__dict__ = loaded_obj.__dict__

    def search(self):
        logger.info('starting search')
        found = 0

        new_links = search()

        for link in new_links:
            if link not in self.links:
                logger.debug('adding new link')
                self.links.append(link)

                partner = Partner()
                partner.update_attribute('links', link)
                logger.debug('adding new partner')
                self.partners.append(partner)
                found += 1

        logger.info('partners found: %s' % found)
        return found

    def update(self):
        updated = 0
        conflicts = 0
        for partner in self.partners:
            updated += partner.update()
            if partner.conflicts:
                conflicts += 1

        logger.info('partners updated: %s, with conflicts: %s' % (updated, conflicts))
        return updated, conflicts
