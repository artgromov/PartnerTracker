import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def update(url):
    if url.startswith('http://dancesport.ru'):
        logger.debug('redirecting to update_from_dancesport(%s)' % url)
        return update_from_dancesport(url)


def update_from_dancesport(url):
    base_url = 'http://dancesport.ru'

    data = {'name': None,
            'links': [url],
            'images': [],
            'videos': [],
            'description': None,
            'birth': None,
            'city': None,
            'country': None,
            'height': None,
            'class_st': None,
            'class_la': None,
            'club': None
            }

    page = requests.get(url)
    logger.debug('updating status code "%s"' % page.status_code)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "html.parser")

        # Get tag <h1> with name
        name = soup.find('h1')
        if name:
            data['name'] = name.text.strip()

        # Get target div <div class="one-adv cf">
        target_div = soup.find('div', {'class': 'one-adv cf'})
        if target_div:

            # Get main image
            image_div = target_div.find('div', {'class': 'img'})
            main_image = image_div.find('img').get('src')
            if main_image != '/images/empty-img.png':
                data['images'].append(base_url + image_div.find('img').get('data-colorbox'))

                images = image_div.find_all('div', {'class': 'one-img cboxElement'})
                if images:
                    for tag in images:
                        data['images'].append(base_url + tag.get('data-colorbox'))

            # Get videos
            videos = target_div.find_all('iframe', {'class': 'youtubeframe'})
            for tag in videos:
                data['videos'].append('https://www.youtube.com/watch?v=' + tag.get('src').split('/')[-1])

            # Get description
            try:
                description = target_div.find('div', {'class': 'descript'}).find('p', {'class': ''}).text
                data['description'] = description.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')

            except AttributeError:
                pass

            # Get notes data
            notes = target_div.find('div', {'class': 'descr'}).find_all('p', {'class': 'note'})
            notes = [i.text.strip().replace(': ', ':') for i in notes]

            # Parse note data
            for i in notes:
                if i.startswith('Год рождения'):
                    data['birth'] = int(i.split(':')[1])
                    continue

                if i.startswith('Город'):
                    data['city'] = i.split(':')[1].split(', ')[0]
                    data['country'] = i.split(':')[1].split(', ')[1]
                    continue

                if i.startswith('Рост'):
                    data['height'] = int(i.split(':')[1].split(' ')[0])
                    continue

                if i.startswith('Класс'):
                    class_string = i.split(':')[1].strip()
                    if class_string.startswith('St'):
                        data['class_st'] = class_string[4]

                        if len(i) > 6:
                            data['class_la'] = class_string[12]

                        continue

                    if class_string.startswith('La'):
                        data['class_la'] = class_string[4]
                        continue

                if i.startswith('Клуб'):
                    data['club'] = i.split(':')[1]
                    continue

                else:
                    continue

        return data
    else:
        logger.error('updating status code "%s"' % page.status_code)
        return False


if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)

    def print_attr(instance):
        print('-'*100)
        print('{:50.50}{}'.format('attribute name', 'value'))
        print('-'*100)
        for k, v in instance.items():
            print('{:50.50}{}'.format(k, v))

    url1 = 'http://dancesport.ru/partners/partners_9324.html'
    url2 = 'http://dancesport.ru/partners/partners_9102.html'
    url3 = 'http://dancesport.ru/partners/partners_9472.html'
    url4 = 'http://dancesport.ru/partners/partners_8837.html'

    print_attr(update(url1))
    print()
    print_attr(update(url2))
    print()
    print_attr(update(url3))
    print()
    print_attr(update(url4))
