from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError
from urllib.parse import urljoin
import pickle
import os
import time
from content import Content

URL = 'https://www.xkcd.com'


class ImageData(Content):
    def __init__(self, data_type):
        super(ImageData, self).__init__(data_type)
        self.website = "www.xkcd.com"
        self.number = None
        self.title = None
        self.link = None
        self.filename = None

    def save(self):
        # Pass a json file and save data of the
        # Content data in json format in the passed
        # file
        pass

    def __str__(self):
        stng = super(ImageData, self).__str__()
        stng += "%s %s\n" % ("Number:", self.number)
        stng += "%s %s\n" % ("Title:", self.title)
        stng += "%s %s\n" % ("Filename:", self.filename)
        stng += "%s %s\n" % ("Link:", self.link)
        return stng


# Download image from the website and return ImageData
def download_image(count=1):
    img_url = urljoin(URL, str(count))

    # Connect to the image url, if cannot connect retry
    # after 30 seconds
    while True:
        try:
            req = requests.get(img_url)
        except ConnectionError:
            print('Error occurred. Trying again in 30s.')
            time.sleep(30)
            continue
        break

    # status code 404 indicates we passed the number of
    # available comics
    if req.status_code == 404:
        print('No More Comics')
        return False

    # Parse the html to collect image data
    soup = BeautifulSoup(req.text, 'lxml')
    comic_title = soup.find(attrs={'id': 'ctitle'})
    comic = soup.find(attrs={'id': 'comic'})

    # store all the image related information in ImageData
    # object
    image = ImageData('media')
    image.number = count
    image.title = comic_title.text
    image.message = comic.img.get('title').split('\n')
    image.link = urljoin('https:', comic.img.get('src'))
    image.format = comic.img.get('src').split('.')[-1]
    image.filename = "xkcd." + image.format
    image.filepath = os.getcwd() + '/' + image.filename

    # write the data to file in chunks
    req = requests.get(image.link, stream=True)
    with open(image.filename, 'wb') as temp:
        for chunk in req.iter_content(chunk_size=1024 * 256):
            temp.write(chunk)
    return image


# def save_image(image, data):
#     count = image.number
#     if count - 1 in data['FavoriteComics']:
#         msg = 'This image is already in your favorites.'
#         title = 'File Exists.'
#         print(title)
#         print(msg)
#     else:
#         from_file = 'temp.' + image.format
#         to_file = image.title.strip('.') + '.' + image.format
#         path = os.path.expanduser('~')
#         path = os.path.join(path, 'Pictures', 'xkcd')
#         to_file = os.path.join(path, to_file)
#         if not os.path.isdir(path):
#             os.makedirs(path)
#         os.rename(from_file, to_file)
#         data['FavoriteComics'].add(count - 1)


# Store the data about the images viewed so far and
# return ImageData
def get_image():

    # Load if we already have any metadata about the
    # images we have retrieved so far, and if not create
    # metadata
    if os.path.isfile('metadata.pkl'):
        with open('metadata.pkl', 'rb') as meta:
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
    with open('metadata.pkl', 'wb') as meta:
        pickle.dump(data, meta)
    return image
