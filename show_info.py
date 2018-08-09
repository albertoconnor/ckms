import requests
from bs4 import BeautifulSoup


def show_info_from_url(url):
    info = {}
    response = requests.get(url)
    if response.status_code != 200:
        return info

    soup = BeautifulSoup(response.content, features="html.parser")
    info['title'] = soup.find(class_="entry-title").text
    info['artist'] = soup.find(rel="author").text

    return info


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
