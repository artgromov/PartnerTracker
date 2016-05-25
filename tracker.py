#!/usr/bin/python3.5

import requests
from bs4 import BeautifulSoup
import yaml
import sys
import webbrowser


STATE = ['init',
         'syn',
         'ack',
         'full',
         'test',
         'ignore',
         'noan',
         'na'
         ]

def to_list(val):
    if isinstance(val, (list, tuple)):
        return list(val)
    elif val is not None:
        return [val]
    else:
        return list()

class PartnerFinder:        
    def __init__(self):
        self.base_url = 'http://dancesport.ru'
        self.search_url = self.base_url + '/partners/?edit=1&sessionsrch=1&country=219&sex=2&city=17849&age_to=1989&age_from=1996&len_from=165&len_to=177&PClass_2[0]=A&PClass_2[1]=S'

        self.objects = []

    def search_for_links(self, url, pos_key='&curPos='):
        pos_val = 0
        partner_urls = []
        while True:
            page = requests.get(url + pos_key + str(pos_val))
            soup = BeautifulSoup(page.text, "html.parser")
            divs = soup.find_all('div', {'class': 'one-result'})
            if len(divs) > 0:
                for i in divs:
                    partner_url = i.find('span', {'class': 'title'}).find('a').get('href')
                    partner_urls.append(self.base_url + partner_url)
            else:
                break
            pos_val += 20
        return partner_urls

    def update_from_yaml(self, filename='partners.yml'):
        updated = 0
        added = 0

        with open(filename, encoding='utf-8') as datafile:
            data = yaml.load(datafile.read())

        for partner in data:
            found_match = False
            for i in self.objects:
                if partner['link'] == i.link:
                    found_match = True
                    updated += i.load_from_dict(partner)
            if not found_match:
                new_partner = Partner()
                new_partner.load_from_dict(partner)
                self.objects.append(new_partner)
                added += 1
        return updated, added

    def update_from_web(self):
        # update existing objects
        updated = 0
        for i in self.objects:
            if i.state != STATE[5]:
                if i.provider == 'dancesport.ru':
                    updated += i.load_from_web(i.link)

        # get search data
        links = self.search_for_links(self.search_url)

        added = 0
        # search for duplicate links, append if not found
        for link in links:
            found_match = False
            for i in self.objects:
                if link == i.link:
                    found_match = True
            if not found_match:
                new_partner = Partner()
                new_partner.load_from_web(link)
                self.objects.append(new_partner)
                added += 1
        return updated, added

    def save_to_yaml(self, filename='partners.yml'):
        data = [i.data for i in self.objects]
        with open(filename, 'w', encoding='utf-8') as datafile:
            yaml.dump(data, datafile, default_flow_style=False, allow_unicode=True, width=1000)

        return len(data)


class Partner:
    def __init__(self):
        self.data = {'link': '',
                     'id': '',
                     'image': '',
                     'name': '',
                     'birth': '',
                     'height': '',
                     'country': '',
                     'city': '',
                     'club': '',
                     'class_st': '',
                     'class_la': '',
                     'description': '',
                     'notes': '',
                     'state': STATE[0],
                     'provider': '',
                     }

    def __getattr__(self, item):
        return self.data[item]

    def __repr__(self):
        return '{id:4} {state:6.6} {name:20} {class_st:1} {class_la:1} {description}. Notes: {notes}'.format(**self.data)

    def load_from_dict(self, new_data):
        updated = 0
        for key in self.data.keys():
            try:
                if self.data[key] != new_data[key]:
                    self.data[key] = new_data[key]
                    updated = 1
            except KeyError:
                pass
        return updated

    def load_from_web(self, link, base_url='http://dancesport.ru'):
        self.data['link'] = link

        new_data = {}

        # Get page, then parse it with bs4
        page = requests.get(self.link)

        if page.status_code == 404:
            new_data['state'] = STATE[7]

        elif page.status_code == 200:
            soup = BeautifulSoup(page.text, "html.parser")

            # Get tag <h1> with name
            new_data['name'] = soup.find('h1').text

            # Get main tag <div class="one-adv cf">
            tag = soup.find('div', {'class': 'one-adv cf'})

            # Get main image
            new_data['image'] = base_url + tag.find('div', {'class': 'img'}).find('img').get('src')

            # Get id
            new_data['id'] = int(tag.find('div', {'class': 'descr'}).find('div', {'class': 'numb'}).text[1:])

            # Get description
            try:
                description = tag.find('div', {'class': 'descript'}).find('p', {'class': ''}).text
                new_data['description'] = description.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
            except AttributeError:
                pass

            # Get notes data
            notes = tag.find('div', {'class': 'descr'}).find_all('p', {'class': 'note'})
            notes = [i.text.strip().replace(': ', ':') for i in notes]

            # Parse note data
            for i in notes:
                if i.startswith('Год рождения'):
                    new_data['birth'] = int(i.split(':')[1])
                    continue
                if i.startswith('Город'):
                    new_data['city'] = i.split(':')[1].split(', ')[0]
                    new_data['country'] = i.split(':')[1].split(', ')[1]
                    continue
                if i.startswith('Рост'):
                    new_data['height'] = int(i.split(':')[1].split(' ')[0])
                    continue
                if i.startswith('Класс'):
                    class_string = i.split(':')[1].strip()
                    if class_string.startswith('St'):
                        new_data['class_st'] = class_string[4]
                        if len(i) > 6:
                            new_data['class_la'] = class_string[12]
                        continue
                    if class_string.startswith('La'):
                        new_data['class_la'] = class_string[4]
                        continue
                if i.startswith('Клуб'):
                    new_data['club'] = i.split(':')[1]
                    continue
                else:
                    continue

        return self.load_from_dict(new_data)


def interactive(partner_finder):

    usage = lambda : print('''Available actions:
    w    - update from web
    y    - update from yaml
    s    - save to yaml
    psl  - print state list
    p[x] - print to console (default states 0 - 4, x = state)
    o[x] - open in default web browser (default states 0 - 4, x = state)
    q - quit''')

    usage()

    while True:
        key = input('Select action: ')

        if key == 'w':
            print('Updating from web...')
            u, a = partner_finder.update_from_web()
            print('Updated: {} Added: {}'.format(u, a))

        elif key == 'y':
            print('Loading from yaml...')
            u, a = partner_finder.update_from_yaml()
            print('Updated: {} Added: {}'.format(u, a))

        elif key == 's':
            print('Saving to yaml...')
            l = partner_finder.save_to_yaml()
            print('Saved: {} lines'.format(l))

        elif key == 'psl':
            print('State list:')
            for n, i in enumerate(STATE):
                print('{} - {}'.format(n, i))

        elif key.startswith('o') or key.startswith('p'):
            operation = key[0]
            start_state = 0
            end_state = 4

            if len(key) == 2 and key[1].isdigit():
                start_state = int(key[1])
                end_state = start_state

            elif len(key) == 3 and key[1].isdigit() and key[2].isdigit():
                start_state = int(key[1])
                end_state = int(key[2])


            states = to_list(STATE[start_state:end_state + 1])

            counter = 0
            for i in partner_finder.objects:
                if i.state in states:
                    counter += 1
                    if operation == 'p':
                        print(i)
                    elif operation == 'o':
                        webbrowser.open(i.link)
            print('Printed {} lines'.format(counter))

        elif key == 'q':
            print('Quitting...')
            sys.exit(0)

        elif key == '':
            pass

        else:
            usage()


if __name__ == '__main__':
    engine = PartnerFinder()
    
    print('Updating from yaml...')
    u, a = engine.update_from_yaml()
    print('Updated: {} Added: {}'.format(u, a))

    interactive(engine)

else:
    pass