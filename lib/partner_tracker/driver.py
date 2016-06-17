import logging
import pickle

from partner_tracker.partner import Partner

logger = logging.getLogger(__name__)


class Driver:
    def __init__(self):
        logger.debug('creating new %s object' % self.__class__.__name__)

        self.searchers = []
        self.providers = []
        self.partners = []

    def save(self, filename='driver.p'):
        logger.debug('saving state to file %s' % filename)
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    def load(self, filename='driver.p'):
        logger.debug('loading state from file %s' % filename)
        with open(filename,'rb') as file:
            loaded_obj = pickle.load(file)
        self.__dict__ = loaded_obj.__dict__

    def add_searcher(self, searcher):
        if searcher not in self.searchers:
            logger.debug('adding new searcher')
            self.searchers.append(searcher)
        else:
            logger.info('searcher is already added')

    def search(self):
        logger.debug('starting search')
        if len(self.searchers) > 0:
            for searcher in self.searchers:
                new_providers = searcher.search()

                for provider in new_providers:
                    if provider not in self.providers:
                        logger.debug('adding new provider with id: "%s"' % provider.id)
                        self.providers.append(provider)

        else:
            logger.info('no searchers attached')

    def update(self):
        logger.debug('starting update')
        for provider in self.providers:
            provider.update()

    def merge(self, force=False):
        for partner in self.partners:
            for provider in partner.providers:
                if not provider.commited:
                    new_data = provider.get_changes()

                    for key, new_value in new_data.items():
                        if key in partner.__dict__:
                            old_value = partner.__dict__[key]

                            if not old_value:
                                partner.__dict__[key] = new_value

                            elif old_value != new_value:
                                if force:
                                    partner.__dict__[key] = new_value
                                else:
                                    while True:
                                        answer = input('Update "{}"="{}" with new value "{}" (y/n): '.format(key, old_value, new_value))
                                        if answer == 'y':
                                            partner.__dict__[key] = new_value
                                            break
                                        elif answer == 'n':
                                            break

                    provider.commit()

    def get_partner_by_id(self, partner_id):
        for partner in self.partners:
            if partner.id == partner_id:
                return partner

    def edit(self, partner_id):
        partner = self.get_partner_by_id(partner_id)
