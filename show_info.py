from email.utils import formatdate
import re
import unicodedata

import requests
from bs4 import BeautifulSoup

from schedules import key_to_datetime


def show_info_from_url(url):
    info = {}
    print('request GET {}'.format(url))
    response = requests.get(url)
    if response.status_code != 200:
        print('request GET {} failed {}'.format(url, response.status_code))
        return info

    soup = BeautifulSoup(response.content, features="html.parser")
    info['title'] = soup.find(class_="entry-title").text
    info['artist'] = soup.find(rel="author").text

    return info


def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    value = (
        unicodedata.normalize('NFKD', value)
        .encode('ascii', 'ignore')
        .decode('ascii')
    )
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


bracket_tag_re = re.compile(r'\(.*\)')


def show_slug_from_name(name):
    name = re.sub(bracket_tag_re, '', name)
    slug_name = slugify(name)

    return slug_name


def show_url_from_name(name):
    slug_name = show_url_from_name(name)
    return 'https://radiowaterloo.ca/category/{}/?tag=about'.format(slug_name)


def start_to_pub_date(starts):
    '''
    source is like 2019-06-24 05:00:00 but we
    need Thu, 21 Dec 2016 16:01:07 +0000
    '''

    show_date = key_to_datetime(starts)

    return formatdate(float(show_date.strftime('%s')))


def generate_tags(show):
    url = show_url_from_name(show['details']['name'])
    if not url:
        return None

    info = show_info_from_url(url)

    show_date = key_to_datetime(show['starts']).date()
    show_title = '{}: {}'.format(
        info['title'],
        show_date.strftime('%B %d %Y')
    )

    pub_date = start_to_pub_date(show['details']['starts'])

    comment = '{}@@{}'.format(url, pub_date)

    tags = {
        'album': info['title'],
        'artist': info['artist'],
        'title': show_title,
        'date': show_date.strftime('%Y'),
        'comment': comment,
    }

    return tags


if __name__ == "__main__":
    response = requests.get(
        'http://radiowaterloo.ca/schedule/about-our-shows/'
    )
    soup = BeautifulSoup(response.content, features="html.parser")

    urls = [
        e.attrs['href']
        for e in
        soup.find_all('a', class_='pt-cv-thumb-default')
    ]
    for url in urls:
        print(url, show_info_from_url(url))
