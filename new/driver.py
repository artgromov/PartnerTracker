from searchers import SearcherDancesportRu
from providers import ProviderDancesportRu
from partner import Partner


class Driver:
    def __init__(self):
        self.log = logging.getLogger(__name__)

        self.searchers = []
        self.providers = []
        self.partners = []

    def search(self):
        for searcher in self.searchers:
            new_providers = searcher.search()

            for new_provider in new_providers:
                if new_provider not in self.providers:
                    new_provider.update()
                    new_partner = Partner()
                    new_partner.providers.append(new_provider)

                    self.providers.append(new_provider)
                    self.partners.append(new_partner)


    def update(self):
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
        partner = get_partner_by_id(partner_id)

        # edit attributes

