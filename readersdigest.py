from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError
import pickle
import random
import os
from content import Content
from datetime import datetime


class JokesData(Content):
    def __init__(self, data_type):
        super(JokesData, self).__init__(data_type)
        self.genre = None
        self.title = None
        self.post_id = None

    def save(self, file):
        # Pass a json file and save data of the
        # Content data in json format in the passed
        # file
        pass

    def __str__(self):
        stng = super(JokesData, self).__str__()
        stng += "%s %s\n" % ("Title:", self.title)
        stng += "%s %s\n" % ("Genre:", self.genre)
        stng += "%s %s\n" % ("Post ID:", self.post_id)
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
def download_jokes(url, joke_type):
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

    for i in range(len(_jokes)):
        _jokes[i][1] = _jokes[i][1].strip('\n').strip(' ')
        _jokes[i][2] = _jokes[i][2].strip('\n').strip(' ').split('\n')

    # Make a list of JokesData
    jokes = []
    for joke in _jokes:
        item = JokesData('text')
        item.title = joke[1]
        item.genre = joke_type.split('/')[-1]
        item.message = ['*' + item.title + '*', '_' + item.genre + '_'] \
            + joke[2]
        item.timestamp = datetime.ctime(datetime.now())
        item.website = 'readersdigest'
        item.post_id = joke[0]
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
