import json
import re
import operator
import shutil
import time
import os
from pathlib import Path
import platform

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

    def __init__(self):
        '''Initializes main_link attribute. '''

        # Extract data from config.json
        dir_path = Path(f"{os.path.dirname(os.path.abspath(__file__))}"
                        "/config.json")
        with open(dir_path) as config:
            data = json.load(config)

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
            self.options = chrome_options

    def convert_to_cbz(self, issue_data):
        '''Convert pages stored in target_path to .cbz file type'''

        issue_path = self.issue_dir(issue_data)
        cbz_dir = os.path.dirname(issue_path)

        shutil.make_archive(Path(f"{cbz_dir}/{issue_data[2]}"), 'zip',
                            issue_path)

        shutil.move(Path(f"{cbz_dir}/{issue_data[2]}.zip"),
                    Path(f"{cbz_dir}/{issue_data[2]}.cbz"))

    def download_all_pages(self, issue_data):
        ''' Download image from link.'''

        issue_path = self.issue_dir(issue_data)
        print(f"Started downloading {issue_data[2]}")

        # Create progress bar that monitors page download.
        with tqdm(total=len(issue_data[0])) as pbar:
            for index, link in enumerate(issue_data[0]):

                # Download image
                number_of_zeroes = len(str(len(issue_data[0])))
                modified_index = str(index).zfill(number_of_zeroes)
                page_path = Path(f"{issue_path}/page{modified_index}.jpg")
                page = requests.get(link, stream=True)
                with open(page_path, 'wb') as file:
                    file.write(page.content)
                pbar.update(1)

        print(f"Finished downloading {issue_data[2]}")

    def get_raw_links_list(self, main_link):
        '''Gathers the html code of the main link.'''
        # A chrome window is opened to bypass cloudflare.
        driver = webdriver.Chrome(executable_path=self.driver_path,
                                  options=self.options)
        driver.set_window_size(300, 500)
        driver.get(main_link)
        # A 60 second margin is given for browser to bypass cloudflare and
        # load readcomiconline.to logo.
        wait = WebDriverWait(driver, 60)
        element = wait.until(ec.visibility_of_element_located(
            (By.LINK_TEXT, "ReadComicOnline.to")))
        time.sleep(0.5)

        # The whole html code is downloaded.
        raw_links_list = driver.find_element_by_class_name("listing")
        raw_links_list = str(raw_links_list.get_attribute('innerHTML'))
        driver.quit()
        return raw_links_list

    def get_partial_issues_links(self, raw_links_list):
        '''Gather all partial individual issues links from html code.'''
        # Re module is used to extract relevant links.
        generic_link = re.compile(r'(?<=")/Comic/.+?id=\d+(?=")', re.I)
        target_links = re.findall(generic_link, raw_links_list)
        partial_issues_links = [partial_link for partial_link in target_links]
        print("All issues links were gathered.")
        return partial_issues_links

    def complete_issues_links(self, partial_issues_links):
        '''Add core link to partial links'''
        core_link = "https://readcomiconline.to"
        issues_links = []
        for link in partial_issues_links:
            full_link = core_link + link
            issues_links.append(full_link)
        return issues_links

    def get_comic_and_issue_name(self, partial_issue_link, raw_links_list):
        '''Finds out comic and issue name from partial_link and main_link.'''

        # Re module is used to get issue and comic name.
        # The comic name is extracted from the link.
        generic_comic_name = re.compile(r"(?<=comic/)(.+?)/(.+?)(?=\?|$)",
                                        re.I)
        comic_name_regex = re.search(generic_comic_name, partial_issue_link)
        comic_name = comic_name_regex.group(1)

        # The issue name is extracted from the raw_links_list.
        link = re.escape(partial_issue_link)
        generic_comic_name = re.compile(
            rf"<.+{link}.+>\s(?P<title>.+?)(<|$)", re.I | re.M)
        issue_name_regex = re.search(generic_comic_name, str(raw_links_list))
        issue_name = issue_name_regex.group("title").strip()

        # Fix presence of forward slash in issue name on mac and linux.
        if (platform.system() == "Darwin") | (platform.system() == "Linux"):
            issue_name = issue_name.replace("/", ":")

        # comic_issue_names[0] is the issue link, comic_issue_names[1]
        # is the comic name and comic_issue_names[2] is the issue name.
        comic_issue_name = [partial_issue_link, comic_name, issue_name]
        return comic_issue_name

    def main_link(self, issue_link):
        '''Returns main link from issue link.'''

        generic_main_link = re.compile(r"https://.+?/.+/.+/", re.I)
        main_link_regex = re.search(generic_main_link, issue_link)
        main_link = main_link_regex.group(0)
        return main_link

    def get_pages_links(self, partial_link, raw_links_list):
        ''' Gather the links of each page of an issue.'''
        # The partial link is completed
        core_link = "https://readcomiconline.to"
        issue_link = core_link + partial_link

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
        read_type = Select(driver.find_element_by_id('selectReadType'))
        read_type.select_by_index(1)
        time.sleep(1)

        # According to config.json the quality of the issue is selected.
        select_quality = Select(driver.find_element_by_id('selectQuality'))
        quality = self.quality
        try:
            select_quality.select_by_value(quality)
        except:
            pass
        time.sleep(1)

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
        comic_issue_name = self.get_comic_and_issue_name(
            partial_link, raw_links_list)
        issue_data = (pages_links, comic_issue_name[1], comic_issue_name[2])
        print(f"All links to pages of {issue_data[2]} were gathered.")
        return issue_data

    def is_comic_downloaded(self, comic_issue_name):
        '''Checks if comic has already been downloaded.'''

        download_path = Path(f"{self.download_dir_path}/{comic_issue_name[1]}"
                             f"/{comic_issue_name[2]}")
        cbz_path = Path(f"{self.download_dir_path}/{comic_issue_name[1]}"
                        f"/{comic_issue_name[2]}.cbz")

        if download_path.exists():
            issue = comic_issue_name[2].replace(":", "/")
            print(f"{issue} has already been downloaded.")
            return True
        elif cbz_path.exists():
            issue = comic_issue_name[2].replace(":", "/")
            issue = comic_issue_name[2]
            print(f"{issue} has already been downloaded.")
            return True
        else:
            return False

    def issue_dir(self, issue_data):
        ''' Creates and returns issue download directory.'''
        issue_path = Path(f"{self.download_dir_path}/"
                          f"{issue_data[1]}/{issue_data[2]}")

        # Only if dir doesn't already exists it is created.
        if not issue_path.exists():
            os.makedirs(issue_path)
        return issue_path

    def keep_only_cbz(self, issue_data):
        '''Keep only .cbz file in issue directory.'''
        issue_path = self.issue_dir(issue_data)
        shutil.rmtree(issue_path)

    def range_select(self, start, ending, raw_links_list, q):
        '''Extracts links from the ocurrence of the first pattern till the 
           ocurrence of the second one.'''

        # Due to RCO inverting the order of issues on their website
        # (issue #134 is shown above issue #123) the ending and start patterns
        # order are reversed.
        range_re = re.compile(rf"(.+)(<.+?{ending})(?=</a>)(.+)"
                              rf"(<.+?{start})(?=</a>)", re.M | re.S | re.I)
        result = re.search(range_re, str(raw_links_list))
        raw_links_list = (result.group(2), result.group(3), result.group(4))
        raw_links_list = "\n".join(raw_links_list)
        q.put(raw_links_list)
