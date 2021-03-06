import argparse
import json
from multiprocessing import Process, Queue
import operator
import os
from pathlib import Path
import sys
import time
import threading

from config_generator import ConfigJSON
from RCO_links import RCO_Comic


def animation(phrase):
    '''Creates loading animation.'''
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

parser.add_argument('-c', '--config', action='store_true', dest="config",
                    help='Edit config file.')
parser.add_argument('--cbz', action='store_true', dest="cbz",
                    help='Convert jpgs to cbz.')
parser.add_argument("-i", "--input",  nargs='+', type=str, dest="input",
                    help="Get comic issues from main link.")
parser.add_argument('-k', '--keep', action='store_true', dest="keep",
                    help='Keep jpgs after conversion.')
parser.add_argument('-r', "--range", nargs=2, type=str,
                    dest="range", help='Start and ending regex to download.')
parser.add_argument('--rt', "--ranget", nargs=3, type=str,
                    dest="ranget", help='Same as -r, but with a third argument'
                    ' that allows user to increase time limit.')
parser.add_argument('-s', "--skip", nargs=1, type=int, default=[""],
                    dest="skip", help='Number of issues to skip.')
parser.add_argument("-x", "--single",  nargs="+", dest="single",
                    help="Get a single issue from a certain "
                    "comic from its link.")
parser.add_argument('-v', '--version', action='store_true', dest="version",
                    help='See current version.')


args = parser.parse_args()
if __name__ == '__main__':
    # multiprocessing.freeze_support() use only to make an execcutable.
    # Check if config.json exists
    if not ConfigJSON().config_exists():
        msg = "\nThere was no config.json file so let's create one.\n"
        print(msg)
        ConfigJSON().config_create()
        raise TypeError

    # Download comic from link.

    if args.input:
        for link in args.input:
            stop_animation = False
            t1 = threading.Thread(target=animation, args=["Fetching links"])
            t1.start()
            time.sleep(1)

            comic = RCO_Comic()
            raw_links_list = comic.get_raw_links_list(link)

            # Range selection
            if args.range:
                # Multiprocessing module is used to figure out if re module
                # hangs.
                start = args.range[0]
                end = args.range[1]
                q = Queue()
                p1 = Process(target=comic.range_select,
                             args=(start, end, raw_links_list, q))
                p1.start()
                p1.join(30)
                if q.empty():
                    p1.terminate()
                    stop_animation = True
                    print("\n")
                    print("Range start or end couldn´t be found in the 30 "
                          "seconds time limit. Please check the spelling or "
                          "increase the time limit with -rt.")
                    sys.exit()
                else:
                    raw_links_list = q.get()

            elif args.ranget:
                # Multiprocessing module is used to figure out if
                # re module hangs.
                start = args.ranget[0]
                end = args.ranget[1]
                q = Queue()
                p1 = Process(target=comic.range_select,
                             args=(start, end, raw_links_list, q))
                p1.start()
                p1.join(int(args.ranget[2]))
                if q.empty():
                    p1.terminate()
                    stop_animation = True
                    print("\n")
                    print("Range start or end couldn´t be found in the "
                          f"{args.ranget[2]} seconds time limit. Please check "
                          "the spelling or increase the time limit.")
                    sys.exit()
                else:
                    raw_links_list = q.get()

            partial_issues_links = list(
                comic.get_partial_issues_links(raw_links_list))
            partial_issues_links.reverse()

            # Ignore skipped links.
            if args.skip[0]:
                partial_issues_links = partial_issues_links[args.skip[0]:]
            # Ignore already downloaded issues links
            issues_ids = [comic.get_comic_and_issue_name(
                link, raw_links_list) for link in partial_issues_links]

            downloaded_issues = [issue_id for issue_id in issues_ids
                                 if comic.is_comic_downloaded(issue_id)]

            links_fetcher = operator.itemgetter(0)
            downloaded_issues_links = [links_fetcher(
                issue) for issue in downloaded_issues]
            for link in partial_issues_links[:]:
                if link in downloaded_issues_links:
                    partial_issues_links.remove(link)
            stop_animation = True
            time.sleep(1)
            print()
            # Continue downloading remaining links.
            for issue_link in partial_issues_links:
                stop_animation = False
                t2 = threading.Thread(target=animation, args=["Loading"])
                t2.start()
                issue_data = comic.get_pages_links(issue_link, raw_links_list)
                stop_animation = True
                comic.issue_dir(issue_data)
                comic.download_all_pages(issue_data)

                # cbz conversion
                if args.cbz:
                    comic.convert_to_cbz(issue_data)
                    if not args.keep:
                        comic.keep_only_cbz(issue_data)

        print("Finished download.")

    if args.config:
        ConfigJSON().edit_config()

    if args.single:
        print("Individual issues will be downloaded.")
        for issue_link in args.single:
            # Allow single comic issue to be downloaded.
            core_link = "https://readcomiconline.to"
            partial_link = issue_link.replace(core_link, "")
            comic = RCO_Comic()
            main_link = comic.main_link(issue_link)
            raw_links_list = comic.get_raw_links_list(main_link)
            issue_name = comic.get_comic_and_issue_name(partial_link,
                                                        raw_links_list)

            if not comic.is_comic_downloaded(issue_name):
                issue_data = comic.get_pages_links(
                    partial_link, raw_links_list)
                comic.issue_dir(issue_data)
                comic.download_all_pages(issue_data)
            else:
                continue
            # cbz conversion
            if args.cbz:
                comic.convert_to_cbz(issue_data)
                if not args.keep:
                    comic.keep_only_cbz(issue_data)
        print("Finished download.")

    if args.version:
        print("\n Version: v1.7.1-alpha\n")
