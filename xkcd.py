from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError
from urllib.parse import urljoin
import pickle
import os
import time
from datetime import datetime
from content import Content

URL = 'https://www.xkcd.com'


class ImageData(Content):
    def __init__(self, data_type='media'):
        super(ImageData, self).__init__()
        self.set_type('media')

    def set_content(self, message=None, number=None,
                    title=None, link=None, filename=None,
                    filepath=None, file_format=None,
                    website=None, timestamp=None):

        self._number = number
        self._title = title
        self._link = link
        self._filename = filename
        super(ImageData, self).set_content(
            message=message,
            filepath=filepath,
            file_format=file_format,
            website=website,
            timestamp=timestamp
        )

    def get_comic_number(self):
        return self._number

    def get_comic_title(self):
        return self._title

    def get_comic_link(self):
        return self._link

    def get_comic_filename(self):
        return self._filename

    def write_to_file(self):
        # write the data to file in chunks
        retries = 20
        while retries > 0:
            try:
                req = requests.get(self._link, stream=True)
                with open(self._filename, 'wb') as temp:
                    for chunk in req.iter_content(chunk_size=1024 * 256):
                        temp.write(chunk)
            except ConnectionError:
                retries -= 1
                time.sleep(5)
                continue
            break

    def __eq__(self, other):
        return self._link == other._link

    def __str__(self):
        stng = super(ImageData, self).__str__()
        stng += "%s %s\n" % ("Number:", self._number)
        stng += "%s %s\n" % ("Title:", self._title)
        stng += "%s %s\n" % ("Filename:", self._filename)
        stng += "%s %s" % ("Link:", self._link)
        return stng

    def __repr__(self):
        stng = super(ImageData, self).__str__()
        stng += "%s %s\n" % ("Number:", self._number)
        stng += "%s %s\n" % ("Title:", self._title)
        stng += "%s %s\n" % ("Filename:", self._filename)
        stng += "%s %s" % ("Link:", self._link)
        return stng

    def save(self):
        # Pass a json file and save data of the
        # Content data in json format in the passed
        # file
        pass


# Downloads page source
def download_image_page_source(img_url):

    # Connect to the image url, if cannot connect retry
    # after 30 seconds
    retries = 30
    req = None
    while retries > 0:
        try:
            req = requests.get(img_url)
        except ConnectionError:
            print('Error occurred. Trying again in 30s.')
            retries -= 1
            time.sleep(30)
            continue
        break

    # Either we could not connect to the page or
    # status code 404 indicates we passed the number of
    # available comics
    if req is None or req.status_code == 404:
        return False

    return req.text


# Download image from the website and return ImageData
def download_image(count=1):

    # Parse the html to collect image data
    img_url = urljoin(URL, str(count))
    page_source = download_image_page_source(img_url)
    soup = BeautifulSoup(page_source, 'lxml')
    comic_title = soup.find(attrs={'id': 'ctitle'})
    comic = soup.find(attrs={'id': 'comic'})

    # store all the image related information in ImageData
    # object
    title = comic_title.text
    msg = comic.img.get('title')
    url = urljoin('https:', comic.img.get('src'))
    fname = comic.img.get('src').split('/')[-1]
    frmt = fname.split('.')[-1]
    fpath = os.getcwd() + '/' + fname
    site = "www.xkcd.com"
    image = ImageData()

    image.set_content(
        message=msg,
        title=title,
        link=url,
        file_format=frmt,
        number=count,
        filename=fname,
        filepath=fpath,
        website=site,
    )

    # write the data to file in chunks
    image.write_to_file()
    return image


# Store the data about the images viewed so far and
# return ImageData
def get_content():

    # Load if we already have any metadata about the
    # images we have retrieved so far, and if not create
    # metadata

    meta_file = 'xkcd.pkl'
    if os.path.isfile(meta_file):
        with open(meta_file, 'rb') as meta:
            data = pickle.load(meta)
    else:
        data = {
            'LastComicPage': 0,
            'FavoriteComics': set(),
            'SharedComics': set(),
            'ComicLimit': 1863,
        }

    # Start from the next comic from the last viewed
    count = data['LastComicPage'] + 1

    image = download_image(count)
    data['LastComicPage'] = count

    # Write the metadata to the file for future use
    with open(meta_file, 'wb') as meta:
        pickle.dump(data, meta)
    return image
