import os
import sys
import requests_cache
import tempfile
from datetime import timedelta
from random import choice
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
import itertools

# Other libraries that can be useful to you
from bs4 import BeautifulSoup
from pprint import pprint  # For pretty print
from random import randint  # For random sleep
from time import sleep  # For hard-pause sleep
from tqdm.notebook import tqdm  # Show loop progress
import winsound  # For audio notification
import pyperclip  # For copying a string to clipboard


def generate_headers(headers_dict_from_browser=None):
    """Generate headers for every time better_request_get() runs. This works for requests not selenium

    Args:
        headers_dict_from_browser (dict): this can be obtained from Chrome
        Inspect tool -> Network tab -> click on the request of the website
        url -> Headers tab -> Request Headers. If not provided, a default
        header will be used. The Request Headers you obtained from the
        browser works better

    Returns:
        headers (dict): the full headers dict now with a randomly picked
        user_agents
    """
    requests_cache.install_cache(
        cache_name=os.path.join(tempfile.gettempdir(), "cnn_cache"),
        expire_after=timedelta(minutes=1),
    )

    user_agents = [
        # Chrome on Windows 10
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
        # Firefox on Macos
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.4; rv:100.0) Gecko/20100101 Firefox/100.0",
    ]
    user_agent = choice(
        user_agents)  # Randomly pick a user agent from user_agents

    if headers_dict_from_browser == None:
        headers = {  # This is the header I obtained from Ageless Patterns and
            # it might not work for other websites
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "www.agelesspatterns.com",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
        }  # I tested that only providing the 'User-Agent' is not enough
    else:
        headers = headers_dict_from_browser
    headers['User-Agent'] = user_agent

    return headers


def xpath_from_soup_element(element):
    """Generate xpath of soup element

    Args:
        element (bs4.element.Tag): bs4 text or node

    Returns:
        return (str): xpath
    """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        """
        @type parent: bs4.element.Tag
        """
        previous = itertools.islice(parent.children, 0,
                                    parent.contents.index(child))
        xpath_tag = child.name
        xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
        components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (
            xpath_tag, xpath_index))
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


def sound_notification():
    for i in range(2):
        freq = 100
        dur = 50
        for i in range(5):
            winsound.Beep(freq, dur)
            freq += 100
            dur += 50
    return 0


def error_sound():
    winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
    return 0


def soup_element_to_clipboard(soup_element):
    pyperclip.copy(str(soup_element))
    return 0


def url_to_category(selenium_driver, url):
    # Srape a given Google map url for the category
    selenium_driver.get(url)  # Navigate to the URL

    parent_element = selenium_driver.find_element(
        By.CLASS_NAME,
        'skqShb '
    )  # Find the specific parent div element with class "skqShb"

    child_element = parent_element.find_element(
        By.XPATH,
        ".//div[@class='fontBodyMedium']"
    )  # Find the specific child div element with class "fontBodyMedium" within
    # the parent element

    return child_element


def scrape_all_categories_from_urls(input_df):
    # Caller function for url_to_category(). It works on all the URL from the
    # column Google Maps URL in input_df and stores all the scraped
    # categories into a new column Extracted Category
    output_df = input_df.copy()

    # Configure Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument(
        '--headless')  # Open Chrome in headless mode for making
    # screenshots. Uncomment this line to hide the browser UI.
    options.add_argument(
        '--start-maximized')  # Maximize the browser window to full screen
    # of your computer
    driver = webdriver.Chrome(options=options)

    extracted_categories = []  # Create a list to store the extracted text

    for url in tqdm(output_df[
                        'Google Maps URL']):  # Iterate over the URLs with
        # tqdm progress bar
        try:
            child_element = url_to_category(driver, url)

            element_text = child_element.text  # Extract the text from the
            # desired element

        except NoSuchElementException:  # This means the location has no
            # category as specified on Google map (usually the case of a
            # residential address)
            element_text = 'No Category'
        except Exception as error:  # For all the other errors than
            # NoSuchElementException
            error_sound()
            print('Unknown error {} occurs. Program is terminated.'.format(
                str(error)))
            sys.exit(1)  # Terminate the program

        extracted_categories.append(
            element_text)  # Append the extracted text to the list

        sleep_interval = randint(1, 2)  # Generate a random sleep interval
        # between 1 and 2 seconds
        sleep(sleep_interval)  # Sleep for the random interval

    output_df[
        'Extracted Category'] = extracted_categories  # Add the extracted text
    # as a new column in the dataframe

    driver.quit()  # Close the browser
    sound_notification()  # Vocally notify the job is done
    return output_df
