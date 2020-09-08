import argparse
import json
import operator
import os
from pathlib import Path
import sys
import time
import threading

from config_generator import ConfigJSON
from RCO_links import RCO_Comic

def animation (phrase):
    animation = "|/-\\"
    idx = 0
    while True:
        print(f'{phrase} {animation[idx % len(animation)]}', end="\r")
        idx += 1
        time.sleep(0.1)
        global stop_animation
        if stop_animation:
            break

# Create terminal UI
parser = argparse.ArgumentParser(
    prog="comic_getter",
    description="comic_getter is a command line tool "
    "to download comics from readcomiconline.to.")

parser.add_argument("-i", "--input",  nargs=1, type=str, dest="input",
                    help="Get comic and all of it's issues from main link.")
parser.add_argument('-c', '--config', action='store_true', dest="config",
                    help='Edit config file.')
parser.add_argument("--single",  nargs=1, dest="single",
                    help="Get a single issue from a certain comic from it's link.")
parser.add_argument('-s', "--skip", nargs=1, type=int, default=[""],
                    dest="skip", help='Number of issues to skip.')

args = parser.parse_args()

# Check if config.json exists
if not ConfigJSON().config_exists():
    msg = "\nThere was no config.json file so let's create one.\n"
    print(msg)
    ConfigJSON().config_create()
    sys.exit()

# Download comic from link.
if args.input:
    stop_animation = False
    t1 = threading.Thread(target=animation, args=["Fetching links"])
    t1.start()
    comic = RCO_Comic(args.input[0])
    issues_links = list(comic.get_issues_links())
    issues_links.reverse()

    # Ignore determined links.
    if args.skip[0]:
        issues_links = issues_links[args.skip[0]:]

    # Delete already downloaded issues links
    issues_identifiers = [comic.get_comic_and_issue_name(
        link) for link in issues_links]
    downloaded_issues = filter(comic.is_comic_downloaded, issues_identifiers)
    links_fetcher = operator.itemgetter(0)
    downloaded_issues_links = [links_fetcher(
        issue) for issue in downloaded_issues]
    for link in issues_links[:]:
        if link in downloaded_issues_links:
            issues_links.remove(link)
    stop_animation = True
    time.sleep(1)
    # Continue downloading remaining links.
    for issue_link in issues_links:
        stop_animation = False
        t2 = threading.Thread(target=animation, args=["Loading"])
        t2.start()
        issue_data = comic.get_pages_links(issue_link)
        stop_animation= True
        comic.download_all_pages(issue_data)

    print("Finished download.")

if args.config:
    ConfigJSON().edit_config()

if args.single:
    #Allow single comic to be downloaded. 
    print("Single issue will be downloaded.")
    comic = RCO_Comic(args.single[0])
    issue_link = args.single[0]
    issue_data = comic.get_pages_links(issue_link)
    comic.download_all_pages(issue_data)
    print("Finished download.")
