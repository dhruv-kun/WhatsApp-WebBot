from bs4 import BeautifulSoup
import pickle
import os
import time
import random
from content import Content
from selenium import webdriver
from datetime import datetime


class QuoteData(Content):
    def __init__(self):
        self.set_type('text')
        super(QuoteData, self).__init__()

    def set_content(self, message=None, author=None,
                    quote_id=None, website=None,
                    quote_link=None, timestamp=None):

        super(QuoteData, self).set_content(
            message=message,
            website=website,
            timestamp=timestamp
        )
        self._message.append("*" + author + "*")
        self._quote_url = quote_link
        self._quote_id = quote_id
        self._author = author

    def get_quote_link(self):
        return self._quote_url

    def get_id(self):
        return self._quote_id

    def get_author(self):
        return self._author

    def save(self):
        # Pass a json file and save data of the
        # Content data in json format in the passed
        # file
        pass

    def __str__(self):
        stng = super(QuoteData, self).__str__()
        stng += "%s %s\n" % ("Author:", self._author)
        stng += "%s %s\n" % ("Quote ID:", self._quote_id)
        stng += "%s %s\n" % ("Qoute URL:", self._quote_url)
        return stng

    def __repr__(self):
        stng = super(QuoteData, self).__str__()
        stng += "%s %s\n" % ("Author:", self._author)
        stng += "%s %s\n" % ("Quote ID:", self._quote_id)
        stng += "%s %s\n" % ("Qoute URL:", self._quote_url)
        return stng


CHROMEPATH = os.getcwd() + '/chromedriver'


def get_driver():
    driver = webdriver.Chrome(CHROMEPATH)
    return driver


# Return all authors' urls
def author_urls(url, limit=-1):
    # Load the given url
    driver = get_driver()
    driver.get(url)

    # Parse the html
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    # Find all the 'span' tags with attribute class=authorContentName
    _author_links = soup.find_all('span', attrs={'class': 'authorContentName'})

    # Common base url for all authors' urls
    base_url = "https://www.brainyquote.com/authors/"

    # Format the author names to get the url endings
    # and return them
    a_urls = []
    for ul in _author_links:
        name = ul.text
        name = name.replace('.', '')
        name = name.replace(' ', '_')
        name = name.lower()
        a_urls.append(base_url + name)
    driver.close()
    if limit > -1:
        a_urls = a_urls[:limit]
    return a_urls


# Loads the full page by scrolling down to bottom of the page
# as this site uses infinite scrolling
def load_page(driver):
    # Scroll till the end of the page
    # Get the current max height of the page
    lastHeight = driver.execute_script("return document.body.scrollHeight")
    while True:

        # Scroll to the max height of the current loaded page
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        # Wait for any new to load
        time.sleep(2)

        # Get the new max height of the page
        newHeight = driver.execute_script("return document.body.scrollHeight")

        # If this fails we have reached the bottom of the page
        if lastHeight == newHeight:
            break
        lastHeight = newHeight
    return driver


# Returns the all quotes of the author who's url is given
def download_quotes(driver, auth_url, limit=-1):
    # Load the given url
    driver.get(auth_url)

    # Scroll down to the very bottom of the page, loading all the dynamic
    # content present, effectively loading the full page
    driver = load_page(driver)

    # Parse the html
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    # Find all the 'a' tags which have attribute title=view quote
    quote_links = soup.find_all('a', attrs={'title': 'view quote'})

    quotes = []

    # Format the links data to get QuoteData and return them

    # Actual number of the quotes is half the length of quote_links
    # rest half is the author's name which is picked the the soup.find_all()
    # so we iterate 2 at a time to get them both
    website = "www.brainyquote.com"
    for i in range(0, len(quote_links), 2):
        item = QuoteData()
        # Format the quote so that it will look nicer in whatsapp where all
        # sentences are on single line
        msg = quote_links[i].text
        link = website + quote_links[i].get('href')
        quote_id = quote_links[i].get('href').replace(
            '/quotes/quotes/', '').replace('.html', '')
        quote_id = quote_id.replace('www.brainyquote.com', '')
        athr = quote_links[i + 1].text
        timestamp = datetime.ctime(datetime.now())

        item.set_content(
            message=msg,
            author=athr,
            quote_link=link,
            timestamp=timestamp,
            quote_id=quote_id,
            website=website
        )

        quotes.append(item)
    if limit > -1:
        quotes = quotes[:limit]
    return quotes


# Returns a quote from website or from off-line file
def get_content():

    # Url where authors names are shown
    url = "https://www.brainyquote.com/"
    # If metadata exists then get data from that that else
    # create data with initial values
    meta_file = 'brainyquote.pkl'
    if os.path.isfile(meta_file):
        with open(meta_file, 'rb') as meta:
            data = pickle.load(meta)
    else:
        # If metadata is not present the create data with all authors' urls
        data = {
            "quotesNotSeen": [],
            "authorsFinshedUrls": set(),
            "authorsUnfinshedUrls": set(author_urls(url + 'authors'))
        }

    driver = None

    # If we have unseen quotes less than 300 fetch some more from the
    # website 10 authors at a time
    while len(data['quotesNotSeen']) < 300:
        driver = get_driver()
        ten_auth_urls = [data['authorsUnfinshedUrls'].pop() for i in range(10)]
        for auth_url in ten_auth_urls:
            data['authorsFinshedUrls'].add(auth_url)
            data['quotesNotSeen'] += download_quotes(driver, auth_url)
        # Shuffle quotes so that quotes from same authors are not
        # sent back to back
        random.shuffle(data['quotesNotSeen'])

    if driver:
        driver.close()

    # Get a quote from the data collected
    quote = data['quotesNotSeen'].pop()

    with open(meta_file, 'wb') as meta:
        pickle.dump(data, meta)

    return quote
