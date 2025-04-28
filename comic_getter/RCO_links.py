import json
import re
import operator
import shutil
import time
import os
from pathlib import Path
import platform
import sys

from tqdm import tqdm
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

# When making exe replace os.path.dirname(os.path.abspath(__file__))
# with  os.path.dirname(sys.executable) here and in config_generator.py
# and import sys.


class RCO_Comic:
    '''Collection of functions that allow to download a 
    readcomiconline comic with all it's issues.'''

    def __init__(self, link):
        '''Initializes main_link attribute. '''

        # Extract data from config.json

        dir_path = Path(f"{os.path.dirname(os.path.abspath(__file__))}"
                        "/config.json")
        with open(dir_path) as config:
            data = json.load(config)

        self.full_link = link
        self.domain = self.get_domain()
        self.main_link = self.get_main_link()

        # Config.json settings.
        self.driver_path = data["chromedriver_path"]
        self.download_dir_path = data["download_dir"]
        self.quality = data["quality"]

        if not data.get("visibility"):
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_experimental_option('excludeSwitches',
                                                   ['enable-logging'])
            self.options = chrome_options
        else:
            chrome_options = Options()
            chrome_options.add_experimental_option('excludeSwitches',
                                                   ['enable-logging'])
            self.options = chrome_options

    def convert_to_cbz(self, issue_data):
        '''Convert pages stored in target_path to .cbz file type'''

        issue_path = self.issue_dir(issue_data, True)
        cbz_dir = os.path.dirname(issue_path)

        shutil.make_archive(Path(f"{cbz_dir}/{issue_data[2]}"), 'zip',
                            issue_path)

        shutil.move(Path(f"{cbz_dir}/{issue_data[2]}.zip"),
                    Path(f"{cbz_dir}/{issue_data[2]}.cbz"))

    def download_issue(self, issue_data):
        ''' Download image from link.'''
        issue_path = self.issue_dir(issue_data)
        print(f"Started downloading {issue_data[2]}")

        # Figure out whether pages have been downloaded previously.
        files_in_issue_path = list(os.walk(issue_path))[0][2]
        pages_downloaded = 0
        for file in files_in_issue_path:
            if file[:4] == "page":
                pages_downloaded += 1

        number_of_zeroes = len(str(len(issue_data[0])))
        index_start = 0 if pages_downloaded == 0 else pages_downloaded-1
        if pages_downloaded != 0:
            last_page_number = str(index_start).zfill(number_of_zeroes)
            os.remove(Path(f"{issue_path}/page{last_page_number}.jpg"))

        # Create progress bar that monitors page download.
        with tqdm(total=len(issue_data[0]), desc="Pages downloaded",
                  leave=False, dynamic_ncols=True, initial=index_start,
                  unit_scale=True, unit="pages") as pbar:
            for index, link in enumerate(issue_data[0][index_start:],
                                         start=index_start):
                # Download page
                modified_index = str(index).zfill(number_of_zeroes)
                page_path = Path(f"{issue_path}/page{modified_index}.jpg")
                page = requests.get(link, stream=True)
                with open(page_path, 'wb') as file:
                    file.write(page.content)
                pbar.update(1)

            # Rename already finished download directory.
            os.rename(issue_path, self.issue_dir(issue_data, True))
        print(f"Finished downloading {issue_data[2]}")

    def get_domain(self):
        '''Use regular expressions to extract domain from url.'''
        pattern = r"(https://|http://)(.+?)(?=/)"
        match = re.search(pattern, self.full_link)
        if match is None:
            print("Not a valid link.")
            sys.exit()
        else:
            domain = match[0]

        return domain

    def get_partial_issue_data(self, partial_link=None, driver=None):
        '''Returns partial name, comic name and issue's name.'''

        if partial_link is None:
            partial_link = self.full_link.replace(self.domain, "")
        if driver is None:
            driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'),
                                      options=self.options)
            driver.get(self.main_link)
            # A 60 second margin is given for browser to bypass cloudflare and
            # load readcomiconline logo.
            wait = WebDriverWait(driver, 60)
            logo = wait.until(ec.visibility_of_element_located(
                (By.CSS_SELECTOR, "a[title='ReadComicOnline - "
                    "Read high quality comic online']")))
            time.sleep(0.5)

        comic_name = driver.find_element(By.CSS_SELECTOR, ".bigChar").text
        issue_name = driver.find_element(By.CSS_SELECTOR, f"a[href='{partial_link}']").text

        comic_name = self.replace_illegal_filename_characters(comic_name)
        issue_name = self.replace_illegal_filename_characters(issue_name)

        return [partial_link, comic_name, issue_name], driver

    def get_raw_links_list(self):
        '''Gathers the html code of the main link.'''

        driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'),
                                  options=self.options)
        driver.set_window_size(300, 500)

        driver.get(self.main_link)
        # A 60 second margin is given for browser to bypass cloudflare and
        # load readcomiconline logo.
        wait = WebDriverWait(driver, 60)
        element = wait.until(ec.visibility_of_element_located(
            (By.CSS_SELECTOR, "a[title='ReadComicOnline - Read high quality comic online']")))
        time.sleep(0.5)

        # The whole html code is downloaded.
        raw_links_list = driver.find_element(By.CLASS_NAME, "listing")
        raw_links_list = str(raw_links_list.get_attribute('innerHTML'))
        driver.quit()
        return raw_links_list

    def get_partial_issues_links(self, raw_links_list):
        '''Gather all partial individual issues links from html code.'''
        # Re module is used to extract relevant links.
        generic_link = re.compile(r'(?<=")/Comic/.+?id=\d+(?=")', re.I)
        target_links = re.findall(generic_link, raw_links_list)
        partial_issues_links = [partial_link for partial_link in target_links]
        return partial_issues_links

    def get_main_link(self):
        '''Returns main link from full link.'''

        generic_main_link = re.compile(
            r"(https://|http://)(.+?/.+?/.+?)(?=/|$)", re.I)
        main_link_regex = re.search(generic_main_link, self.full_link)
        main_link = main_link_regex[0]
        return main_link

    def get_pages_links(self, partial_link=None):
        ''' Gather the links of each page of an issue.'''
        # The partial link is completed
        if partial_link is not None:
            issue_link = self.domain + partial_link
        else:
            issue_link = self.full_link

        driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'),
                                  options=self.options)
        driver.set_window_size(300, 500)
        driver.get(issue_link)

        # A 3600 second = 1 hour time gap is given for browser to bypass
        # cloudflare and for browser to fetch all issues pages before
        # triggering an exception. Such a time is never to be reached
        # and as soon as these events happen the program will continue.
        wait = WebDriverWait(driver, 3600)
        wait.until(ec.visibility_of_element_located(
            (By.CSS_SELECTOR, "a[title='ReadComicOnline - Read high quality comic online']")))

        # An option to load all pages of the issue in the same tab is selected.
        read_type = Select(driver.find_element(By.ID, 'selectReadType'))
        read_type.select_by_index(1)
        time.sleep(1)

        # According to config.json the quality of the issue is selected.
        select_quality = Select(driver.find_element(By.ID, 'selectQuality'))
        quality = self.quality
        try:
            select_quality.select_by_value(quality)
        except:
            pass
        time.sleep(1)
        
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")

        # An explicit wait is trigger to wait for imgLoader to disappear.
        wait.until(ec.invisibility_of_element((By.ID, "imgLoader")))
        element = driver.find_element(By.ID, "divImage")
        raw_pages_links = element.get_attribute('innerHTML')
        driver.quit()

        # Re module is used to extract relevant links.
        generic_page_link = re.compile(
            r'(?<=")https://2.bp.blogspot.com/.+?(?=")', re.I)
        pages_links = re.findall(generic_page_link, raw_pages_links)

        return pages_links

    def is_comic_downloaded(self, comic_issue_name):
        '''Checks if comic has already been downloaded.'''
        download_path = Path(f"{self.download_dir_path}/{comic_issue_name[1]}"
                             f"/{comic_issue_name[2]}")
        cbz_path = Path(f"{self.download_dir_path}/{comic_issue_name[1]}"
                        f"/{comic_issue_name[2]}.cbz")
        issue = comic_issue_name[2]

        if download_path.exists():
            print(f"{issue} has already been downloaded.")
            return True
        elif cbz_path.exists():
            print(f"{issue} has already been downloaded.")
            return True
        else:
            return False

    def is_comic_partially_downloaded(self, comic_issue_name):
        '''Checks if comic has been partially downloaded.'''

        download_path = Path(f"{self.download_dir_path}/{comic_issue_name[1]}"
                             f"/{comic_issue_name[2]}_dw")
        issue = comic_issue_name[2]

        if download_path.exists():
            return True
        else:
            return False

    def issue_dir(self, issue_data, downloaded=False):
        ''' Creates and returns issue download directory.'''
        issue_path = Path(f"{self.download_dir_path}/"
                          f"{issue_data[1]}/{issue_data[2]}_dw")

        # Only if dir doesn't already exists it is created.
        if downloaded:
            issue_path = Path(f"{self.download_dir_path}/"
                              f"{issue_data[1]}/{issue_data[2]}")
        elif not issue_path.exists():
            os.makedirs(issue_path)

        return issue_path

    def keep_only_cbz(self, issue_data):
        '''Keep only .cbz file in issue directory.'''
        issue_path = self.issue_dir(issue_data, True)
        shutil.rmtree(issue_path)

    def range_select(self, raw_links_list, q, start, ending=None,):
        '''Extracts links from the ocurrence of the first pattern till the 
           ocurrence of the second one.'''

        # Due to RCO inverting the order of issues on their website
        # (issue #134 is shown above issue #123) the ending and start patterns
        # order are reversed.
        range_re = ""
        if ending:
            range_re = re.compile(rf".+(<.+?{ending}.+?<.+?{start}.+?</a>)",
                                  re.M | re.S | re.I)
        else:
            range_re =re.compile(rf".+(<.+?{start}.+?</a>)",
                                  re.M | re.S | re.I)
        result = re.search(range_re, str(raw_links_list))
        raw_links_list = (result.group(1))
        q.put(raw_links_list)

    def replace_illegal_filename_characters(self, word):
        # Replaces forbidden filename characters with
        word = word.replace(u":", "\u2236")
        word = word.replace(u"/", "\u2215")
        word = word.replace(u"?", "\uFE56")
        word = word.replace(u"%", "\uFE6A")
        word = word.replace(u"\\", "\u2216")
        word = word.replace(u"|", "\u23A5")
        word = word.replace(u"&", "\uFE60")
        word = word.replace(u"<", "\uFE64")
        word = word.replace(u">", "\uFE65")
        word = word.replace(u"\"", "\u02ba")
        word = word.replace(u"*", "\u2217")
        return word
