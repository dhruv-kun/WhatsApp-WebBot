from bs4 import BeautifulSoup
import pickle
import os
import time
import random
from content import Content
from selenium import webdriver
from datetime import datetime


class QuoteData(Content):
    def __init__(self, data_type):
        super(QuoteData, self).__init__(data_type)
        self.author = None
        self.quote_id = None

    def save(self):
        # Pass a json file and save data of the
        # Content data in json format in the passed
        # file
        pass

    def __str__(self):
        stng = super(QuoteData, self).__str__()
        stng += "%s %s\n" % ("Author:", self.author)
        stng += "%s %s\n" % ("Quote ID:", self.quote_id)
        return stng


# Return all authors' urls
def author_urls(driver, url):
    # Load the given url
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
    return set(a_urls)


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
def download_quotes(driver, auth_url):
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
    for i in range(0, len(quote_links), 2):
        item = QuoteData('text')
        # Format the quote so that it will look nicer in whatsapp where all
        # sentences are on single line
        item.message = quote_links[i].text.replace('.', '.\n')
        item.message = quote_links[i].text.split('\n')

        # Authors name
        item.author = quote_links[i + 1].text

        # Formating to emphasis author on the whatsapp
        # *msg* makes the msg look bold
        item.message += ["*" + item.author + "*"]

        # Extra data for module's usage
        item.website = "www.brainyquote.com"
        item.link = item.website + quote_links[i].get('href')
        item.timestamp = datetime.ctime(datetime.now())

        item.quote_id = quote_links[i].get('href')
        item.quote_id = item.quote_id.replace('/quotes/quotes/', '')
        item.quote_id = item.quote_id.replace('.html', '')
        quotes.append(item)
    return quotes


# Returns a quote from website or from off-line file
def get_content():

    # Url where authors names are shown
    url = "https://www.brainyquote.com/quotes/favorites.html"
    chrome_path = os.getcwd() + '/chromedriver'
    driver = None
    # If metadata exists then get data from that that else
    # create data with initial values
    meta_file = 'brainyquote.pkl'
    if os.path.isfile(meta_file):
        with open(meta_file, 'rb') as meta:
            data = pickle.load(meta)
    else:
        # If metadata is not present the create data with all authors' urls
        driver = webdriver.Chrome(chrome_path)
        data = {
            "quotesNotSeen": [],
            "authorsFinshedUrls": set(),
            "authorsUnfinshedUrls": author_urls(driver, url)
        }
        driver.close()
        driver = None

    # If we have unseen quotes less than 300 fetch some more from the
    # website 10 authors at a time
    while len(data['quotesNotSeen']) < 300:
        driver = webdriver.Chrome(chrome_path)
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
