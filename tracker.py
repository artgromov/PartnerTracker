#!/usr/bin/python3.5

import requests
from bs4 import BeautifulSoup
import yaml
import sys
import webbrowser


scripted = False


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
            if not i.ignored:
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

    def dump_to_yaml(self, filename='partners.yml'):
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
                     'closed': False,
                     'notes': '',
                     'wrote_times': '',
                     'ignored': False
                     }

    def __getattr__(self, item):
        return self.data[item]

    def __repr__(self):
        return '{id:4} {name:20} {class_st:1} {class_la:1} {link}\nDescription: {description}\nNotes: {notes}\n'.format(**self.data)

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
            new_data['closed'] = True

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
                if i.startswith('St'):
                    new_data['class_st'] = i[4]
                    if len(i) > 6:
                        new_data['class_la'] = i[12]
                    continue
                if i.startswith('La'):
                    new_data['class_la'] = i[4]
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
    d    - dump to yaml
    p[x] - print to console (not ignored and not closed, x = number of times wrote)
    o[x] - open in default web browser (not ignored and not closed, x = number of times wrote)
    q - quit''')

    usage()

    while True:
        key = input('Select action: ')

        if key == 'w':
            print('Updating from web...')
            u, a = partner_finder.update_from_web()
            print('Updated: {} Added: {}'.format(u, a))

        elif key == 'y':
            print('Updating from yaml...')
            u, a = partner_finder.update_from_yaml()
            print('Updated: {} Added: {}'.format(u, a))

        elif key == 'd':
            print('Dumping to yaml...')
            l = partner_finder.dump_to_yaml()
            print('Dumped: {} lines'.format(l))

        elif key == 'pi':
            for i in partner_finder.objects:
                if i.ignored and not i.closed:
                    print(i)

        elif key.startswith('o') or key.startswith('p'):
            if len(key) == 1:
                operation = key[0]
                count = None
            elif len(key) == 2 and key[1].isdigit():
                operation = key[0]
                count = int(key[1])

            for i in partner_finder.objects:
                selected = False
                if not i.ignored and not i.closed:
                    if count:
                        if i.wrote_times == count:
                            selected = True
                    else:
                        selected = True

                if selected:
                    if operation == 'p':
                        print(i)
                    elif operation == 'o':
                        webbrowser.open(i.link)

        elif key == 'q':
            print('Quitting...')
            sys.exit(0)

        else:
            usage()


def update_and_open(partner_finder):
    print('Updating from yaml...')
    u, a = partner_finder.update_from_yaml()
    print('Updated: {} Added: {}'.format(u, a))

    print('Updating from web...')
    u, a = partner_finder.update_from_web()
    print('Updated: {} Added: {}'.format(u, a))

    print('Dumping to yaml...')
    l = partner_finder.dump_to_yaml()
    print('Dumped: {} lines'.format(l))

    active = [i for i in partner_finder.objects if not i.ignored and not i.closed]
    print('Opening {} active ads in firefox...'.format(len(active)))
    for i in active:
        Popen(r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe ' + i.link, stdout=DEVNULL, stderr=DEVNULL)

    sys.exit(0)


if __name__ == '__main__':
    engine = PartnerFinder()

    if not scripted:
        interactive(engine)
    else:
        update_and_open(engine)
