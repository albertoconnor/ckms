
import requests
from bs4 import BeautifulSoup

from schedules import key_to_datetime


def show_info_from_url(url):
    info = {}
    response = requests.get(url)
    if response.status_code != 200:
        return info

    soup = BeautifulSoup(response.content, features="html.parser")
    info['title'] = soup.find(class_="entry-title").text
    info['artist'] = soup.find(rel="author").text

    return info


def generate_tags(show):
    url = show['url']
    if not url:
        return None

    info = show_info_from_url(url)

    show_date = key_to_datetime(show['starts']).date()
    show_title = '{}: {}'.format(
        info['title'],
        show_date.strftime('%B %d %Y')
    )

    tags = {
        'album': info['title'],
        'artist': info['artist'],
        'title': show_title,
        'date': show_date.strftime('%Y'),
    }

    return tags


if __name__ == "__main__":
    response = requests.get('http://radiowaterloo.ca/schedule/about-our-shows/')
    soup = BeautifulSoup(response.content, features="html.parser")

    urls = [
        e.attrs['href']
        for e in
        soup.find_all('a', class_='pt-cv-thumb-default')
    ]
    for url in urls:
        print(url, show_info_from_url(url))
