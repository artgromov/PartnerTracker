import logging
import pickle

from partner_tracker.partner import Partner

logger = logging.getLogger(__name__)


class Driver:
    def __init__(self):
        self.searchers = []
        self.providers = []
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

    def add_searcher(self, searcher):
        if searcher not in self.searchers:
            logger.info('attaching new searcher')
            self.searchers.append(searcher)

    def search(self):
        logger.info('starting search')
        found = 0
        if len(self.searchers) > 0:
            for searcher in self.searchers:
                new_providers = searcher.search()

                for provider in new_providers:
                    if provider not in self.providers:
                        logger.debug('adding new provider')
                        self.providers.append(provider)

                        partner = Partner()
                        partner.add_provider(provider)
                        logger.debug('adding new partner')
                        self.partners.append(partner)
                        found += 1

        else:
            logger.error('no searchers attached')

        logger.info('partners found: %s' % found)
        return found

    def update(self):
        logger.info('starting update')
        updated = 0
        conflicts = 0
        for partner in self.partners:
            updated += partner.update()
            if partner.conflicts:
                conflicts += 1

        logger.info('partners updated: %s, with conflicts: %s' % (updated, conflicts))
        return updated, conflicts
