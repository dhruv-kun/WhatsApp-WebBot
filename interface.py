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
import readersdigest


# List of Websites from which the data is collected
ALLSITES = [
    xkcd,
    brainyquote,
    readersdigest,
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

    item = []
    message, targets = [], []
    # If there are no messages initially in Slave group, return None, None
    timestamp = -1
    if len(messages_inview) > 0:
        item = messages_inview[-1].text.split('\n')
        message, target = item[:-1], item[-1]
        targets = target.split(' ')
        timestamp = messages_datetime_inview[-1].text
        timestamp = datetime.strptime(timestamp, "%I:%M %p").time()
    else:
        return None, None

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


# Helper function for get_all_users
# returns the list of names present in the search query result
# of get_all_users
def get_names(driver):
    names = []
    try:
        names_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='chat-title']")))
        names = [i.text for i in names_elem]
    except TimeoutException as e:
        print("Nothing found")
    return set(names)


# returns all the unique user names from the contact search feature
def get_all_users(driver):

    # New chat allows to get all the user names and avoids group names
    # This finds and clicks New chat button
    try:
        new_chat = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@title='New chat']")))
        new_chat.click()
        time.sleep(1)
    except TimeoutException as e:
        raise(Exception('New chat button not found'))

    # After New chat clicked, this searches user names by typing all 2
    # combinations of alphabets and get_names gives all the names which are
    # visible on the screen
    # A better approach would be to scroll through the contact names but i
    # don't know how to do that :(
    try:
        all_usernames = set()
        for i in range(26):
            contact_search = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@title='Search contacts']")))
            contact_search.click()
            time.sleep(1)
            for j in range(26):
                user_name = chr(ord('a') + i) + chr(ord('a') + j)
                contact_search.send_keys(user_name)
                time.sleep(1)
                all_usernames |= get_usernames(driver)
                try:
                    close_search = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//button[@class='icon-close-search']")))
                    close_search.click()
                    time.sleep(1)
                except TimeoutException as e:
                    pass
    except Exception as e:
        print(e)

    return all_usernames


# Create a simplified ID - NAME dictionary, where ID is about
# 3-5 characters and where first 3 characters are chosen from the NAME
# and last 1-2 characters are numbers if NAMES collide
def make_cheatsheet(driver):
    usernames = get_all_users(driver)

    targets = {}
    for name in usernames:
        first, second, *rest = name.split(' ')
        key = first.upper()[:2]
        if second:
            key += second.upper()[0]
        else:
            key = first[2].upper()
        count = 0
        while key in targets:
            if count:
                key = key[:-1] + str(count)
            else:
                key += '1'
            count += 1
        targets[key] = name

    # This is for sending to Master group for reference
    item = Content('text')
    item.message = []
    for key, value in sorted(targets.items()):
        msg = "{:<15} {:<15}".format(key, value)
        item.message.append(msg)
    item.timestamp = datetime.ctime(datetime.now())
    return targets, item


# Driver program which will run this whole system
def main():
    # If metadata exists then get data from that that else
    # create data with initial values
    meta_file = 'whatsapp.pkl'
    if os.path.isfile(meta_file):
        with open(meta_file, 'rb') as meta:
            data = pickle.load(meta)
    else:
        data = {
            "targets": [],
            "allSentMessages": [],
            "lastSentMessageTime": -1
        }

    # Pause time between messages
    PAUSE = 15 * 60
    REPEAT = 3
    try:
        driver = login()
        target = 'Master'
        if len(data['targets']) == 0:
            data['targets'], cheat_content = make_cheatsheet(driver)
            try:
                send(driver, 'Master', cheat_content)
            except Exception as e:
                raise(e)
        while True:
            for i in range(REPEAT):
                try:
                    site = random.choice(ALLSITES)
                    item = site.get_content()
                    send(driver, target, item)
                except Exception as e:
                    print(e)
                time.sleep(PAUSE)
            item, ids = recieve(driver, 'Slave')
            if item:
                if data['lastSentMessageTime'] == -1 \
                        or item.timestamp > data['lastSentMessageTime']:
                    if ids[0] == 'ALL':
                        ids = data['targets'].keys()
                    elif ids[0] == 'QUIT':
                        break
                    for id_ in ids:
                        try:
                            send(driver, data['targets'][id_], item)
                            data['allSentMessages'].append(item)
                        except Exception as e:
                            print(e)
                    data['lastSentMessageTime'] = item.timestamp
    except KeyboardInterrupt:
        print('Program Ended')
    finally:
        with open(meta_file, 'wb') as meta:
            pickle.dump(data, meta)
        logout(driver)


if __name__ == "__main__":
    main()
