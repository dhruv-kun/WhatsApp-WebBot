from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError
import pickle
import random
import os
from content import Content
from datetime import datetime


class JokesData(Content):
    def __init__(self):
        self.set_type('text')
        super(JokesData, self).__init__()

    def set_content(self, message, title,
                    genre, post_id,
                    website, timestamp):
        super(JokesData, self).set_content(
            message=message,
            website=website,
            timestamp=timestamp
        )
        self._message = ['*' + title + '*', '_' + genre + '_'] \
            + self._message
        self._title = title
        self._post_id = post_id
        self._genre = genre

    def get_title(self):
        return self._title

    def get_id(self):
        return self._post_id

    def get_genre(self):
        return self._genre

    def save(self, file):
        # Pass a json file and save data of the
        # Content data in json format in the passed
        # file
        pass

    def __str__(self):
        stng = super(JokesData, self).__str__()
        stng += "%s %s\n" % ("Title:", self._title)
        stng += "%s %s\n" % ("Genre:", self._genre)
        stng += "%s %s" % ("Post ID:", self._post_id)
        return stng

    def __repr__(self):
        stng = super(JokesData, self).__str__()
        stng += "%s %s\n" % ("Title:", self._title)
        stng += "%s %s\n" % ("Genre:", self._genre)
        stng += "%s %s" % ("Post ID:", self._post_id)
        return stng


# Connect to the URL and return BeautifulSoup object of the html
def get_soup(url):
    while True:
        try:
            req = requests.get(url)
        except ConnectionError:
            continue
        break
    soup = BeautifulSoup(req.text, 'lxml')
    return soup


# Download Jokes and makes JokesData object for each joke, and returns a
# list of JokesData
def download_jokes(url, joke_type, limit=-1):
    # Append url extension to the base
    url += '/jokes' + joke_type

    soup = get_soup(url)

    # Find tags with class='jokes-river'
    joke_articles = soup.find_all('article', attrs={'class': 'jokes-river'})

    # Get joke content and joke title
    _jokes = [[i.get('id'), i.header.text, i.div.text] for i in joke_articles]

    # Restrict max length of jokes
    char_limit = 1000
    _jokes = [i for i in _jokes if len(i[1]) < char_limit]

    if limit > -1:
        _jokes = _jokes[:limit]

    for i in range(len(_jokes)):
        _jokes[i][1] = _jokes[i][1].strip('\n').strip(' ')
        _jokes[i][2] = _jokes[i][2].strip('\n').strip(' ')

    # Make a list of JokesData
    website = 'readersdigest'
    jokes = []
    for joke in _jokes:
        item = JokesData()

        post_id, title, message = joke
        genre = joke_type.split('/')[-1]

        timestamp = datetime.ctime(datetime.now())

        item.set_content(
            title=title,
            genre=genre,
            message=message,
            timestamp=timestamp,
            website=website,
            post_id=post_id
        )
        jokes.append(item)
    return jokes


# Return a joke from the web or the off-line storage and refill
# the off-line storage with new jokes as needed
def get_content():
    # Load if we already have any metadata about the
    # images we have retrieved so far, and if not create
    # metadata
    meta_file = 'readersdigest.pkl'
    url = 'https://www.rd.com'
    if os.path.isfile(meta_file):
        with open(meta_file, 'rb') as meta:
            data = pickle.load(meta)
    else:
        data = {
            'JokesSeen': [],
            'JokesNotSeen': [],
            'JokeTypesNotFetched': ['/knock-knock',
                                    '/corny',
                                    '/one-liners',
                                    '/riddles']
        }

    # If unseen jokes are less than 100 and if there are any types
    # left for scraping, scrape those types of jokes from the web
    while len(data['JokesNotSeen']) < 100 \
            and len(data['JokeTypesNotFetched']) > 0:
        joke_type = data['JokeTypesNotFetched'].pop()
        data['JokesNotSeen'] += download_jokes(url, joke_type)

    # Shuffle so we can return different types every time this is called
    random.shuffle(data['JokesNotSeen'])

    joke = data['JokesNotSeen'].pop()
    data['JokesSeen'].append(joke)

    with open(meta_file, 'wb') as meta:
        pickle.dump(data, meta)

    return joke
