import time
import os
import random
import pickle
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from content import Content
import xkcd
import brainyquote

# Dictionary of the people to send messages
TARGETS = {
    "BAK": "Badal DTU",
    "ASK": "Ashutosh Kumar",
    "AKD": "Akshay Kapoor DTU",
    "MAK": "Mhd Ashar",
    "SAC": "Sachit Bhai",
    "KEC": "Keerti Chechi",
    "SAK": "Sakshi",
    "PRD": "Priya",
    "NID": "Nikhil DTU A2",
    "SOT": "Sonu Thakur",
    "GID": "Gitesh DTU",
    "MOD": "Mohit IT",
    "DHD": "Dhruv Anand DTU",
    "HID": "Hitesh Kumar A2",
    "SAD": "Sachin DTU",
    "NID": "Nikita DTU",
    "AVD": "Ajay Verma DTU",
    "AKE": "Akash ECE",
    "RAB": "Ramya",
    "KRD": "Krishan DTU",
    "KAD": "Karan Goyal DTU",
    "RAD": "Rajat Kumar DTU B2",
    "SAS": "Saarthak",
    "HES": "Hemant",
    "KAN": "Kannan",
    "REP": "Rejith Prabhakar",
    "MAM": "Mamma",
    "PAP": "PAP",
    "VIN": "Vibhu",
    "NEB": "Neha",
    "LAD": "Lakhan Bakshi DTU",
    "NIB": "Nibin",
}

# List of Websites from which the data is collected
ALLSITES = [
    "xkcd",
    "brainyquote",
]


# Finds target by searching from the search bar
def find_user(driver, target):
    try:
        # Get the search bar element and enter the user name
        # into it, if the user name is present it will be visible
        # for further actions
        search_bar = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "input-search")))
        search_bar.send_keys(target)

        # Wait for the user to get visible
        time.sleep(1)
        try:
            # Search for user in the visible window and if found
            # click on them
            user = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[@title='%s']" % target)))
            user.click()

            # Wait to complete the above action
            time.sleep(1)
        except TimeoutException as e:
            raise(Exception('User Not found %s' % target))
        finally:
            # Clear the input after entering into search bar for next search
            # Find close search bar icon and click if found
            try:
                close_search_bar = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//button[@class='icon-close-search']")))
                close_search_bar.click()
                time.sleep(1)
            except TimeoutException as e:
                pass
    except TimeoutException as e:
        raise(Exception('Search bar not found'))


# Sends the media to target
def send(driver, target, item):

    # Find user
    find_user(driver, target)

    # Sending media, documents is different than sending text
    if item.data_type == 'text':
        # Find and click where we can enter text
        inpt = driver.find_element_by_xpath(
            "//div[@contenteditable='true']")
        inpt.click()

        # For multi-line text press shift then enter to move to
        # next line
        for i in item.message:
            inpt.send_keys(i)
            inpt.send_keys(Keys.SHIFT, Keys.RETURN)

        # Send the written text
        inpt.send_keys(Keys.RETURN)

    else:
        # Find the button from which we can attach file
        attach_menu = driver.find_element_by_xpath("//button[@title='Attach']")
        attach_menu.click()
        time.sleep(0.5)

        # Different buttons for media, document
        if item.data_type == 'media':
            inpt = driver.find_element_by_xpath(
                "//input[@accept='image/*,video/*']")
        elif item.data_type == 'document':
            inpt = driver.find_element_by_xpath(
                "//input[@accept='*']")

        inpt.send_keys(item.filepath)
        time.sleep(2)
        if item.message is not None:
            try:
                caption = driver.find_element_by_xpath(
                    "//div[@contenteditable='true']")
                caption.click()
            except Exception as e:
                print('Error')
                raise(e)

            # For multi-line text press shift then enter to move to
            # next line
            for i in item.message:
                caption.send_keys(i)
                caption.send_keys(Keys.SHIFT, Keys.RETURN)

        # Wait for the send button to be visible after
        # uploading content usually takes less than 10 seconds
        # and click send
        try:
            send = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[@data-icon='send-light']")))
            send.click()

            # Apparently only clicking the send button will not
            # do the job, we have to wait a bit to complete the
            # process
            time.sleep(2)

            # This is for closing the attachment menu, sloppy but
            # does the job for now
            driver.find_element_by_xpath(
                "//div[@contenteditable='true']").click()

            # Wait for any next activity
            time.sleep(1)
            # Add the the receiver's name to the sent list
            item.sent += [target]
        except TimeoutException as e:
            raise(Exception('File upload Not Completed'))


# Reads the last text message from the target
# For now this will read from slave only and
# and will only read text messages
def recieve(driver, target='Slave'):
    # Find the target from which we read
    find_user(driver, target)

    # Get the list of text messages present in the visible
    # window
    messages_inview = driver.find_elements_by_xpath(
        "//div[@class='message-text']")
    messages_datetime_inview = driver.find_elements_by_xpath(
        "//span[@class='message-datetime']")

    # Special formating is used to make sense of the text
    # Last line will contain targets and all the lines above
    # it will contain the text message
    # Eg.
    #     We should not give up and we should not allow the
    #     problem to defeat us.
    #     A. P. J. Abdul Kalam
    #     PRD RAB SAS
    # targets = ['PRD', 'RAB', 'SAS']
    item = messages_inview[-1].text.split('\n')
    message, target = item[:-1], item[-1]
    targets = target.split(' ')

    timestamp = messages_datetime_inview[-1].text
    timestamp = datetime.strptime(timestamp, "%I:%M %p").time()

    # Make a Content object for the above message so that it
    # can be sent to targets using send()
    item = Content('text')
    item.message = message
    item.timestamp = timestamp
    return item, targets


# Login to "https://web.whatsapp.com/"
def login():

    # Path to the chrome driver
    chrome_path = os.getcwd() + '/chromedriver'
    driver = webdriver.Chrome(chrome_path)

    driver.get('https://web.whatsapp.com')

    # Login in 30 seconds or less using QR code
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "intro-body")))
    except TimeoutException as e:
        raise(Exception('Could Not Login'))
        driver.close()
    return driver


# Log out and close the driver after use
def logout(driver):
    try:
        # Find the menu item in 10s or less and click on it
        menu = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@title='Menu']")))
        menu.click()

        # Wait for the dropdown menu to open
        time.sleep(2)
        try:
            # Find and click the logout button in 10s or less
            lgt = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@title='Log out']")))
            lgt.click()

            # Wait to get logged out
            time.sleep(2)
        except TimeoutException as e:
            raise(Exception("Log out button not found"))
    except TimeoutException as e:
        raise(Exception('Menu not found'))
    finally:
        driver.close()


# Driver program which will run this whole system
def main():
    # If metadata exists then get data from that that else
    # create data with initial values
    if os.path.isfile('whatsapp.pkl'):
        with open('whatsapp.pkl') as meta:
            data = pickle.load(meta)
    else:
        data = {
            "allSentMessages": [],
            "lastSentMessageTime": -1
        }

    # Pause time between messages
    PAUSE = 5 * 60
    try:
        driver = login()
        target = 'Master'
        while True:
            for i in range(5):
                try:
                    site = random.choice(ALLSITES)
                    if site == 'xkcd':
                        item = xkcd.get_image()
                        print("In xkcd")
                    elif site == 'brainyquote':
                        item = brainyquote.get_quote()
                        print("In Brainyquote")
                    send(driver, target, item)
                except Exception as e:
                    print(e)
                time.sleep(PAUSE)
            item, ids = recieve(driver, 'Slave')
            if data['lastSentMessageTime'] == -1 \
                    or item.timestamp > data['lastSentMessageTime']:
                if ids[0] == 'ALL':
                    ids = TARGETS.keys()
                for id_ in ids:
                    try:
                        send(driver, TARGETS[id_], item)
                        data['allSentMessages'].append(item)
                    except Exception as e:
                        print(e)
                data['lastSentMessageTime'] = item.timestamp
    except KeyboardInterrupt:
        with open('whatsapp.pkl', 'wb') as meta:
            pickle.dump(data, meta)
    finally:
        logout(driver)


if __name__ == "__main__":
    main()
