import os
import sys
import json
from pathlib import Path

#Make sure viibility evaluates false by default.
class ConfigJSON:
    '''Group of all functions that create and modify Config.json .'''

    def __init__(self):
        '''Initialize main dir path used in several methods.'''
        self.dir = os.path.dirname(os.path.abspath(__file__))

    def change(self):
        '''Allows user to select an attribute in cofig.json and change it.'''

        while True:
            print("0. Change download dir.")
            print("1. Change chromedriver path.")
            print("2. Change visibility.")
            print("3. Quit\n")

            option = input(" >>  ")
            print()
            if not option or "3" == option:
                print("Done.\n")
                sys.exit()

            elif option == "0":
                self.option_create("download_dir")

            elif option == "1":
                self.option_create("chromedriver_path")

            elif option == "2":
                self.option_create("visibility")

            else:
                print("Input not valid. \n")

    def chromedriver_path(self):
        '''Choose chromedriver dir.'''
        print("Write the path to the chromedriver:\n (Have in mind the program"
              " only checks if the path leads to a file and not a dir. Also "
              "check that chromedriver version matches your chrome browser.")
        while True:
            chromedriver_path = input(" >>  ")
            if chromedriver_path:
                if os.path.isfile(chromedriver_path.strip()):
                    return chromedriver_path.strip()
                else:
                    print("Path invalid. Please try again:")
            else:
                print("Path is required.")

    def config_create(self):
        '''Creates config.json.'''
        config_path = os.path.join(self.dir, "config.json")
        download_dir = self.download_dir()
        print()
        chromedriver_path = self.chromedriver_path()
        print()
        visibility = self.visibility()
        data = {
            "download_dir": str(download_dir),
            "chromedriver_path": str(chromedriver_path),
            "visibility": visibility
        }
        with open(config_path, "w") as config:
            json.dump(data, config)
        print("\nDone.\n")

    def config_exists(self):
        '''Check if movies_list.json exists.'''
        main_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(main_path, "config.json")
        return os.access(config_path, os.R_OK)

    def download_dir(self):
        '''Set download dir.'''
        print("Write the path to the download dir:\n (By default the "
              "program will create a dir to contain comic and issues in "
              "the cwd).\n")
        while True:
            download_dir = input(" >>  ")
            if download_dir:
                if os.path.isdir(download_dir.strip()):
                    print(f"Your download dir is: {download_dir}")
                    return download_dir.strip()
                else:
                    print("Path invalid. Please try again:")
            else:
                download_dir = os.getcwd()
                print(f"Your download dir is: {download_dir}")
                return download_dir

    def edit_config(self):
        '''Edit config.json file.'''

        if not self.config_exists():
            self.config_create()
            sys.exit()

        while True:
            print("\nPrevious config.json found. What do you want to do?\n")
            print("0. Edit config file.")
            print("1. Start new config file.")
            print("2. Quit.\n")

            option = input(" >>  ")
            print()
            if not option or "2" == option:
                print("Done.\n")
                sys.exit()
            elif "0" == option:
                self.change()
                print("Done.\n")
            elif "1" == option:
                os.remove(Path(f"{self.dir}/config.json"))
                self.config_create()
                sys.exit()
            else:
                print("Input not valid. \n")

    def option_create(self, name):
        '''Create option to be displayed when change is triggered.'''

        config_path = os.path.join(self.dir, "config.json")
        value = getattr(self, name)()
        with open(config_path) as config:
            data = json.load(config)
            data[name] = value
        with open(config_path, "w") as config:
            json.dump(data, config)
        print("\nDone\n")

    def visibility(self):
        ''' Make user determine if browser opened windows are to be displayed.)
        '''
        print("Choose if you want to see the windows opened by the browser."
            "Answer yes/no. (By default the answer is no)")

        while True:
            visibility = input(" >>  ")
            if visibility:
                if visibility == "yes":
                    return True
                elif visibility == "no":
                    return False                
                else:
                    print("Path invalid. Please try again:")
            else:
                return 
