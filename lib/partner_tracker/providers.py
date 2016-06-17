import logging
from abc import *
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Provider(metaclass=ABCMeta):
    def __init__(self):
        logger.debug('creating new %s object' % self.__class__.__name__)
        self.id = None

        # updating process state vars
        self.changed = set()
        self.commited = True

    def __eq__(self, other):
        if self.id == other.id:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.id)

    def commit(self):
        self.changed = set()
        self.commited = True

    def get_changes(self):
        return {key: self.__dict__[key] for key in self.changed}

    def update_attribute(self, name, new_value):
        if new_value:
            old_value = self.__getattribute__(name)

            if isinstance(old_value, set):
                if new_value not in old_value:
                    logger.debug('updating attribute: "%s" with value: "%s" ' % (name, new_value))
                    old_value.add(new_value)
                    self.changed.add(name)

            else:
                if old_value != new_value:
                    logger.debug('updating attribute: "%s" with value: "%s" ' % (name, new_value))
                    self.__setattr__(name, new_value)
                    self.changed.add(name)

    @abstractmethod
    def update(self):
        raise NotImplementedError


class ProviderDancesportRu(Provider):
    base_url = 'http://dancesport.ru'

    def __init__(self, url, date):
        Provider.__init__(self)
        self.id = url
        self.date = date

        self.number = None
        self.name = None
        self.images = set()
        self.videos = set()
        self.description = None
        self.birth = None
        self.city = None
        self.country = None
        self.height = None
        self.class_st = None
        self.class_la = None
        self.club = None

    def __repr__(self):
        return 'ProviderDancesportRu(%s, %s)' %(self.id, self.date)

    def __str__(self):
        string = ''
        for key in sorted(self.__dict__.keys()):
            string += '%s: %s\n' % (key, self.__dict__[key])
        return string.rstrip()

    def update(self):
        page = requests.get(self.id)
        logger.debug('updating status code "%s"' % page.status_code)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, "html.parser")

            # Get tag <h1> with name
            name = soup.find('h1')
            if name:
                name = name.text.strip()
                self.update_attribute('name', name)

            # Get target div <div class="one-adv cf">
            target_div = soup.find('div', {'class': 'one-adv cf'})
            if target_div:

                # Get main image
                image_div = target_div.find('div', {'class': 'img'})
                main_image = image_div.find('img').get('src')
                if main_image != '/images/empty-img.png':
                    image = self.base_url + image_div.find('img').get('data-colorbox')
                    self.update_attribute('images', image)

                    images = image_div.find_all('div',{'class': 'one-img cboxElement'})
                    if images:
                        for tag in images:
                            image = self.base_url + tag.get('data-colorbox')
                            self.update_attribute('images', image)

                # Get videos
                videos = target_div.find_all('iframe',{'class':'youtubeframe'})
                for tag in videos:
                    video = 'https://www.youtube.com/watch?v=' + tag.get('src').split('/')[-1]
                    self.update_attribute('videos', video)

                # Get number
                number = int(target_div.find('div', {'class': 'descr'}).find('div', {'class': 'numb'}).text[1:])
                self.update_attribute('number', number)

                # Get description
                try:
                    description = target_div.find('div', {'class': 'descript'}).find('p', {'class': ''}).text
                    description = description.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
                    self.update_attribute('description', description)

                except AttributeError:
                    pass

                # Get notes data
                notes = target_div.find('div', {'class': 'descr'}).find_all('p', {'class': 'note'})
                notes = [i.text.strip().replace(': ', ':') for i in notes]

                # Parse note data
                for i in notes:
                    if i.startswith('Год рождения'):
                        birth = int(i.split(':')[1])
                        self.update_attribute('birth', birth)
                        continue

                    if i.startswith('Город'):
                        city = i.split(':')[1].split(', ')[0]
                        self.update_attribute('city', city)

                        country = i.split(':')[1].split(', ')[1]
                        self.update_attribute('country', country)

                        continue

                    if i.startswith('Рост'):
                        height = int(i.split(':')[1].split(' ')[0])
                        self.update_attribute('height', height)

                        continue

                    if i.startswith('Класс'):
                        class_string = i.split(':')[1].strip()
                        if class_string.startswith('St'):
                            class_st = class_string[4]
                            self.update_attribute('class_st', class_st)

                            if len(i) > 6:
                                class_la = class_string[12]
                                self.update_attribute('class_la', class_la)

                            continue

                        if class_string.startswith('La'):
                            class_la = class_string[4]
                            self.update_attribute('class_la', class_la)

                            continue

                    if i.startswith('Клуб'):
                        club = i.split(':')[1]
                        self.update_attribute('club', club)

                        continue

                    else:
                        continue

        else:
            logger.error('updating status code "%s"' % page.status_code)

        if len(self.changed) > 0:
            self.commited = False

        return self.changed


if __name__ == '__main__':
    from time import sleep
    from copy import deepcopy

    logging.basicConfig(level=logging.DEBUG)

    def print_attr(instance):
        print('-'*100)
        print('{:50.50}{}'.format('attribute name','value'))
        print('-'*100)
        for k, v in instance.__dict__.items():
            print('{:50.50}{}'.format(k,v))

    url1 = 'http://dancesport.ru/partners/partners_9324.html'
    url2 = 'http://dancesport.ru/partners/partners_9102.html'
    url3 = 'http://dancesport.ru/partners/partners_9472.html'
    provider = ProviderDancesportRu(url3,'dumbdatestring')
    privider2 = ProviderDancesportRu(url2,'dumbdatestring')

    a = {provider}

    print_attr(provider)
    sleep(1)
    provider.update()
    sleep(1)
    print_attr(provider)

    print(provider in a)
    print(privider2 in a)
