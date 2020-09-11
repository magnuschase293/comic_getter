import json
import re
import operator
import time
import os
from pathlib import Path


from tqdm import tqdm
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

class RCO_Comic:
    '''Collection of functions that allow to download a 
    readcomiconline.to comic with all it's issues.'''

    def __init__(self, main_link):
        '''Initializes main_link attribute. '''

        # Seed link that contains all the links of the different issues.
        self.main_link = main_link

        # Extract data from config.json
        dir_path = Path(f"{os.path.dirname(os.path.abspath(__file__))}"
                        "/config.json")
        with open(dir_path) as config:
            data = json.load(config)

        self.driver_path = data["chromedriver_path"]
        self.download_directory_path = data["download_dir"]

        if not data.get("visibility"):
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_experimental_option('excludeSwitches',
                                                   ['enable-logging'])
            self.options = chrome_options

        else:
            chrome_options = Options()
            self.options = chrome_options

    def download_all_pages(self, issue_data):
        ''' Download image from link.'''

        download_path = Path(f"{self.download_directory_path}/"
                             f"{issue_data[1]}/{issue_data[2]}")
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        else:
            print(f"{issue_data[2]} has already been downloaded.")
            return
        print(f"Started downloading {issue_data[2]}")

        # Create progress bar that monitors page download.
        with tqdm(total=len(issue_data[0])) as pbar:
            for index, link in enumerate(issue_data[0]):

                # Download image
                page_path = Path(f"{download_path}/page{index}.jpg")
                page = requests.get(link, stream=True)
                with open(page_path, 'wb') as file:
                    file.write(page.content)
                pbar.update(1)

        print(f"Finished downloading {issue_data[2]}")

    def get_issues_links(self):
        '''Gather all individual issues links from main link.'''

        # A chrome window is opened to bypass cloudflare.
        driver = webdriver.Chrome(executable_path=self.driver_path,
                                  options=self.options)
        driver.set_window_size(300, 500)
        driver.get(self.main_link)
        # A 60 second margin is given for browser to bypass cloudflare and
        # load readcomiconline.to logo.
        wait = WebDriverWait(driver, 60)
        element = wait.until(ec.visibility_of_element_located(
            (By.LINK_TEXT, "ReadComicOnline.to")))
        # The whole html code is downloaded.
        body = driver.find_element_by_tag_name("body")
        body = str(body.get_attribute('innerHTML'))
        driver.quit()

        # Re module is used to extract relevant links.
        core_link = "https://readcomiconline.to"
        generic_link = re.compile(r'(?<=")/Comic/.+?id=\d+(?=")', re.I)
        target_links = re.findall(generic_link, body)
        issues_links = []
        for link in target_links:
            full_link = core_link + link
            issues_links.append(full_link)
        print("All issues links were gathered.")
        return issues_links

    def get_pages_links(self, issue_link):
        ''' Gather the links of each page of an issue.'''

        driver = webdriver.Chrome(executable_path=self.driver_path,
                                  options=self.options)
        driver.set_window_size(300, 500)
        driver.get(issue_link)

        # A 3600 second = 1 hour time gap is given for browser to bypass
        # cloudflare and for browser to fetch all issues pages before
        # triggering an exception. Such a time is never to be reached
        # and as soon as these events happen the program will continue.
        wait = WebDriverWait(driver, 3600)
        wait.until(ec.visibility_of_element_located(
            (By.LINK_TEXT, "ReadComicOnline.to")))

        # An option to load all pages of the issue in the same tab is selected.
        select = Select(driver.find_element_by_id('selectReadType'))
        select.select_by_index(1)
        time.sleep(2)

        # An explicit wait is trigger to wait for imgLoader to disappear.
        wait.until(ec.invisibility_of_element((By.ID, "imgLoader")))
        element = driver.find_element_by_id("divImage")
        raw_pages_links = element.get_attribute('innerHTML')
        driver.quit()

        # Re module is used to extract relevant links.
        generic_page_link = re.compile(
            r'(?<=")https://2.bp.blogspot.com/.+?(?=")', re.I)
        pages_links = re.findall(generic_page_link, raw_pages_links)

        # Pages links, comic name and issue name are packed inside issue_data
        # tuple.
        comic_issue_name = self.get_comic_and_issue_name(issue_link)
        issue_data = (pages_links, comic_issue_name[1], comic_issue_name[2])
        print(f"All links to pages of {issue_data[2]} were gathered.")
        return issue_data

    def get_comic_and_issue_name(self, issue_link):
        '''Finds out comic and issue name from link.'''

        # Re module is used to get issue and comic name.
        generic_comic_name = re.compile(r"(?<=comic/)(.+?)/(.+?)(?=\?)", re.I)
        name_and_issue = re.search(generic_comic_name, issue_link)

        # comic_issue_names[0] is the comic's link name, comic_issue_names[1]
        # is the comic name and comic_issue_names[2] is the issues name.
        comic_issue_name = [issue_link, name_and_issue[1], name_and_issue[2]]
        return comic_issue_name

    def is_comic_downloaded(self, comic_issue_name):
        '''Checks if comic has already been downloaded.'''

        download_path = Path(f"{self.download_directory_path}"
                             f"/{comic_issue_name[1]}/{comic_issue_name[2]}")
        if os.path.exists(download_path):
            print(f"{comic_issue_name[2]} has already been downloaded.")
            return True
        else:
            return False