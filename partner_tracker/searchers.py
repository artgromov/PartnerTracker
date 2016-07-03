import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def search():
    return search_on_dancesport()


def search_on_dancesport():
    base_url = 'http://dancesport.ru'
    query_url = '/partners/?edit=1&sessionsrch=1&country=219&sex=2&city=17849&age_to=1989&age_from=1996&len_from=165&len_to=177&PClass_2[]=B&PClass_2[]=A&PClass_2[]=S'
    search_url = base_url + query_url

    logger.debug('searching on "%s"' % search_url)
    pos_val = 0
    pos_key = '&curPos='

    links = []
    while True:
        page = requests.get(search_url + pos_key + str(pos_val))

        soup = BeautifulSoup(page.text, 'html.parser')

        divs = soup.find_all('div', {'class': 'one-result'})
        if len(divs) > 0:
            for tag in divs:
                partner_url = base_url + tag.find('span', {'class': 'title'}).find('a').get('href')
                if not partner_url:
                    partner_url = base_url + tag.find('span', {'class': 'title advbg'}).find('a').get('href')

                links.append(partner_url)

        else:
            break

        pos_val += 20

    return links


if __name__ == '__main__':
    test = search_on_dancesport()
    print('\n'.join(test))
