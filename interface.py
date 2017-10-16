import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from content import Content
import xkcd


def send(driver, target, item):
    # Find target user and click
    try:
        user = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[@title='%s']" % target)))
        user.click()
    except TimeoutException as e:
        raise('User Not found')

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
            inpt.send_keys(Keys.SHIFT)
            inpt.send_keys(Keys.RETURN)

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

            # The last RETURN after the message sends the message
            # creating problem for the following code who's only
            # job is to send the complete message (image, text)
            # So we send all lines except the last line and send the
            # last line without RETURN
            for i in item.message[:-1]:
                caption.send_keys(i)
                caption.send_keys(Keys.SHIFT)
                caption.send_keys(Keys.RETURN)
            caption.send_keys(item.message[-1])

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
        except TimeoutException as e:
            raise('File upload Not Completed')


def login():

    # Path to the chrome driver
    driver = webdriver.Chrome(
           "/home/dhruv/Workspace/Github Projects/Whatsapp Automation/chromedriver")
    driver.get('https://web.whatsapp.com')

    # Login in 20 seconds or less using QR code
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "intro-body")))
    except TimeoutException as e:
        driver.close()
        raise('Could Not Login')
    return driver

