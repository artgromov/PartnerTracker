from abc import *
import logging
import requests
from bs4 import BeautifulSoup



class Provider(metaclass = ABCMeta):
    def __init__(self):
        self.log = logging.getLogger(__name__)

    @abstractmethod
    def update(self):
        raise NotImplementedError


class DancesportRu(Provider):
    base_url = 'http://dancesport.ru'

    def __init__(self, url):
        Provider.__init__(self)
        self.url = url

        self.full_name = None
        self.images = set()
        self.number = None
        self.description = None
        self.birth = None
        self.city = None
        self.country = None
        self.height = None
        self.class_st = None
        self.class_la = None
        self.club = None

        self.date = None

        self.changed = set()

    def update_attribute(self, name, new):
        self.log.debug('trying to update "{}" with: "{}" '.format(name, new))

        if new:
            old = self.__getattribute__(name)

            if isinstance(old, set):
                if new not in old:
                    old.add(new)
                    self.changed.add(name)

            else:
                if old != new:
                    self.__setattr__(name, new)        
                    self.changed.add(name)

    def update(self):
        self.changed = set()
        
        page = requests.get(self.url)
        self.log.debug('responce code "{}"'.format(page.status_code))
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, "html.parser")

            # Get tag <h1> with name
            full_name = soup.find('h1')
            if full_name:
                full_name = full_name.text.strip()
                self.update_attribute('full_name', full_name)

            # Get target div <div class="one-adv cf">
            target_div = soup.find('div', {'class': 'one-adv cf'})
            if target_div:

                # Get main image
                main_image = target_div.find('div', {'class': 'img'}).find('img').get('src')
                if main_image != '/images/empty-img.png':
                    main_image = self.base_url + main_image
                    self.update_attribute('images', main_image)

                # Get id
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
            self.log.error('cannot load page "{}"'.format(self.url))

        return self.changed


if __name__ == '__main__':
    from time import sleep

    logging.basicConfig(level=logging.DEBUG)

    def print_diff(init, upd):
        print('-'*150)
        print('attribute name'.ljust(50) + 'init value'.ljust(50) + 'updated value'.ljust(50))
        print('-'*150)
        for key in init.keys():
            print(key.ljust(50) + str(init[key]).ljust(50) + str(upd[key]).ljust(50))

    url = 'http://dancesport.ru/partners/partners_8897.html'
    provider = DancesportRu(url)

    init_attrs = provider.__dict__.copy()
    provider.update()
    upd_attrs = provider.__dict__.copy()

    sleep(2)
    print_diff(init_attrs, upd_attrs)
    