import logging
from abc import *
import requests
from bs4 import BeautifulSoup

from partner_tracker.providers import ProviderDancesportRu

logger = logging.getLogger(__name__)


class Searcher(metaclass = ABCMeta):
    def __init__(self):
        logger.debug('creating new %s object' % self.__class__.__name__)

    @abstractmethod
    def search(self):
        raise NotImplementedError


class SearcherDancesportRu(Searcher):
    base_url = 'http://dancesport.ru'
    query_url = '/partners/?edit=1&sessionsrch=1&country=219&sex=2&city=17849&age_to=1989&age_from=1996&len_from=165&len_to=177&PClass_2[0]=A&PClass_2[1]=S'

    def __init__(self):
        Searcher.__init__(self)
        self.search_url = self.base_url + self.query_url

    def search(self):
        logger.debug('searching on "%s"' % self.search_url)
        pos_val = 0
        pos_key = '&curPos='

        new_providers = []
        while True:
            page = requests.get(self.search_url + pos_key + str(pos_val))

            soup = BeautifulSoup(page.text, "html.parser")

            divs = soup.find_all('div', {'class': 'one-result'})
            if len(divs) > 0:
                for tag in divs:
                    partner_url = self.base_url + tag.find('span', {'class': 'title'}).find('a').get('href')
                    if not partner_url:
                        partner_url = self.base_url + tag.find('span', {'class': 'title advbg'}).find('a').get('href')

                    partner_date = tag.find('span', {'class': 'partner-reg-time'}).text

                    new_provider = ProviderDancesportRu(partner_url, partner_date)

                    new_providers.append(new_provider)

            else:
                break

            pos_val += 20

        return new_providers
