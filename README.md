<img src="https://user-images.githubusercontent.com/65515378/93205017-78c53300-f72d-11ea-9cc2-8a3e252c10b1.jpg"  height="263" />

# Comic Getter
Comic Getter is a Command Line Interface (CLI) script written in python that allows users to download comics from readcomiconline.to. It has been tested on MacOS Catalina and Windows 10, but theoretically it should work on every OS.

## Table of Content
* [Installation](#Installation)
    * [Python 3](#Python-3)
    * [PyPI Dependencies](#PyPI-Dependencies)
    * [Comic Getter executable](#Comic-Getter-executable)
    * [Google Chrome and Chromedriver](#Google-Chrome-and-Chromedriver)
* [Usage](#Usage)
    * [Command Line Commands](#Command-Line-Commands)
    * [First time around](#First-time-around)
    * [Examples](#Examples)
      * [Basic commands](#Basic-commands)
      * [CBZ comic conversion](#CBZ-comic-conversion)
      * [Download several comics or issues](#Download-several-comics-or-issues-at-the-same-time)
      * [Range selection](#Range-selection)
      * [Version](#Version)  
* [Features](#Features)
* [Troubleshooting](#Troubleshooting)
* [Issues and Suggestions](#Issues-and-Sugestions)
* [License](#License)
* [Donations](#Donations)

## Installation

There are two options either you proceed to install python and all of the script dependencies or if you are running windows you can download and execute comic_getter.exe. I recommend the first option because the executable will be updated less often than the actual script. Further instructions below:

### Python 3

The script requires python 3.x to run. I leave a link [here](https://www.python.org/downloads/) to the official web page from which one can download the installer.

### PyPI Dependencies

Comic Getter depends on several different packages available in PyPI. If python 3 is already installed, one can simply use the package manager pip3 to install all the dependencies listed.

```bash
pip3 install -r requirements.txt
```
Is important to have in mind requirements.txt should be replaced with the path to requirements.txt.

### Comic Getter executable

In order to run Comic Getter executable you can skip installing Python 3 and the PyPi dependencies. You will only need to download [comic_getter.exe](https://github.com/magnuschase293/comic_getter/releases/tag/v1.0.1). Have in mind Comic Getter depends on flags and parameters given through the command line so it won't work if you just double click it, the excutable must be run through the cmd.

### Google Chrome and Chromedriver

Comic Getter works with Selenium package to bypass cloudflare simulating to be a user that opens Google Chrome. Thus, it requires for Google Chrome and Chromedriver to be installed and the Chromedriver must match your Google Chrome's version. 

* [Here](https://www.google.com/chrome/) is the link to chrome installer.

To check what Google Chrome version is installed an individual needs to press the three dot icon on the top right corner of any chrome tab, open the help sub menu and select "about Google Chrome" option.

<img width="720" alt="Screen Shot 2020-07-10 at 19 23 08" src="https://user-images.githubusercontent.com/65515378/87235165-6803e400-c3af-11ea-8d45-35a7aa0e82dc.png">

Only the first 2 digits in version, below the chrome icon, matter.

<img width="720" alt="Screen Shot 2020-07-10 at 19 23 18" src="https://user-images.githubusercontent.com/65515378/87235168-73570f80-c3af-11ea-909e-925c3e44c776.png">

* [Here](https://sites.google.com/chromium.org/driver/) is the link to different chromedriver versions and installers.

## Usage

### Command Line Arguments
```bash
optional arguments:
optional arguments:
  -h, --help            show this help message and exit
  -c, --config          Edit config file.
  --cbz                 Convert jpgs to cbz.
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Get comic issues from main link.
  -k, --keep            Keep jpgs after conversion.
  -r RANGE RANGE, --range RANGE RANGE
                        Start and ending regex to download.
  --rt RANGET RANGET RANGET, --ranget RANGET RANGET RANGET
                        Same as -r, but with a third argument that allows user
                        to increase time limit.
  -s SKIP, --skip SKIP  Number of issues to skip.
  -x SINGLE [SINGLE ...], --single SINGLE [SINGLE ...]
                        Get a single issue from a certain comic from its link.
  -v, --version         See current version.
  ```
### First Time Around
The first time comic_getter.py is run it will prompt users to fill certain fields (download directory path and chromedriver path). 

* __Download directory path__: the location of the directory where comics will be downloaded. By default the comics are downloaded in the CWD.
* __Chromedriver path__: the location of the chromedriver. It has no default value and the program will not work if the path is not inputed.
* __Visibility__: the program depends on browser opening windows there is no way to avoid it, but the user may not want to see the windows pop up one by one and that's the aim of this field. By default windows will not be displayed (It only accepts yes/no answer).
* __Quality__: the script allows users to choose the quality of comics based on RCO options high quality or low quality.

### Examples

#### Basic commands
Like every other python script it can be executed with python or python 3 command followed by the path to main.py then the corresponding flag and the variable value, if any is required.

For instance, if all issues of [Joker: Last Laugh](https://readcomiconline.to/Comic/Joker-Last-Laugh) are to be downloaded, the following command should do the work:

```bash
python3 path/to/__main__.py -i https://readcomiconline.to/Comic/Joker-Last-Laugh
```
If not all issues, but a single one is required [Issue-4](https://readcomiconline.to/Comic/Joker-Last-Laugh/Issue-4?id=45924) there are three very similar ways of doing this. The first escapes the question mark character with a backlash (question mark has a particular behavior in bash/zsh and if not escaped the program won't work). The second relies on link being inside single or double inverted commas, thus terminal/cmd treats it as a string. Lastly, the link can be shortened deleting everything from the question mark to the end and it should also work. In each of them --single can be replaced with -x without any problems.

```bash
python3 path/to/__main__.py --single https://readcomiconline.to/Comic/Joker-Last-Laugh/Issue-4\?id=45924
```

```bash
python3 path/to/__main__.py --single "https://readcomiconline.to/Comic/Joker-Last-Laugh/Issue-4?id=45924"
```

```bash
python3 path/to/__main__.py --single "https://readcomiconline.to/Comic/Joker-Last-Laugh/Issue-4"
```

If the first 3 issues are not wanted, the -s flag can be used:

```bash
python3 path/to/__main__.py -i https://readcomiconline.to/Comic/Joker-Last-Laugh -s 3
```

If a change is needed to be done to config.json, the -c flag should be used:

```bash
python3 path/to/__main__.py -c
```

In the case you are using the executable the examples are almost the same, but replace:

```bash
python3 path/to/__main__.py 
```
with:
```bash
path/to/comic_getter.exe 
```

#### CBZ comic conversion

You can convert all issues to .cbz file format when downloaded by adding the --cbz flag. By default the jpg file of each page will be deleted, but you can keep them adding the -k flag. 

Using once again [Joker: Last Laugh](https://readcomiconline.to/Comic/Joker-Last-Laugh) as an example:

```bash
python3 path/to/__main__.py -i https://readcomiconline.to/Comic/Joker-Last-Laugh --cbz -k
```

#### Download several comics or issues at the same time

The -i and --single flags allow for several comics/issues to be inputed at once. For instance if the user wants to download [Joker: Last Laugh issue-4](https://readcomiconline.to/Comic/Joker-Last-Laugh/Issue-4) and [Iron Squad Issue 5](https://readcomiconline.to/Comic/Iron-Squad/Issue-5) he can do the following:

```bash
python3 path/to/__main__.py --single https://readcomiconline.to/Comic/Joker-Last-Laugh/Issue-4 https://readcomiconline.to/Comic/Iron-Squad/Issue-5 --cbz
```

Have in mind --cbz and -k flags will affect both comics/issues in such scenario.

#### Range selection

The -r and --rt flags allow users to select a range of issues to be downloaded. The first two arguments of -r and --rt are the start and ending regular expression patterns, respectively. The script looks for this patterns in the list of issues present at the main link. Have in mind capital letters are ignored, but otherwise the patterns must be an exact match. The larger the pattern the more chances it won't repeat and it will determine the range correctly. 

In order for users to have a better experience once they get used to RCO issues naming system I decided to reverse the order in which arguments need to be introduced. Let me explain this a little bit better. 

If the user wants to download [Wolverine (1988)](https://readcomiconline.to/Comic/Wolverine-1988) issue #2 to issue #12 in RCO he would find the following list:
<img width="748" alt="Screen Shot 2020-10-12 at 16 05 18" src="https://user-images.githubusercontent.com/65515378/95784804-e6bc3600-0caa-11eb-8092-40805f563978.png">

By inputing the following code the issues will be downloaded:
```bash
python3 path/to/__main__.py -i https://readcomiconline.to/Comic/Wolverine-1988 -r "#2" "#12"
```
Notice the inverted commas are added for the command line to consider each pattern a single string and ignore any spaces or special characters in the patterns.

If you wanted to select only issue #2 of [Wolverine (1988)](https://readcomiconline.to/Comic/Wolverine-1988) using range select you should type the following command:
```bash
python3 path/to/__main__.py -i https://readcomiconline.to/Comic/Wolverine-1988 -r "#2"
```

Both -r and --rt are really similar the only difference lies in the fact that --rt has an extra argument to expand the 30 seconds timeout for re module to find the start and ending pattern.

#### Version

The -v flag was implemented in order for you to quickly check what version of the program you have:

```bash
python3 path/to/__main__.py -v
```

## Features

Almost every feature has already been explained, but here is a short list that shows them all:

* Choose between high and low quality.
* Convert downloaded comics to cbz file format.
* Download a single issue of a comic.
* Download all issues from a single comic in readcomiconline.to .
* Download multiple comics and issues at once.
* Range select issues through start and ending arguments.
* Resume download.
* Skip unwanted comics.

## Troubleshooting

I have found two bugs after several iterations of the program. The first happened when readcomiconline.to triggered a reCAPTCHA that needs to be bypassed manually either on Google Chrome or the Automated Chrome Tab (the one opened by selenium). After that I simply restarted the script and it continued downloading. A more drastic approach that may work is to change the IP using a VPN after an arbitrary number of downloads, but it has not been tested. If windows aren't visible you'll have to turn visibility on in order to fill the captcha.

The other problem I have encountered with was a 503 Error that I believe happened due to the host (readcomiconline.to) adding a new comic to the site so the server was, for a minute or two, down. After waiting for a while I ran the program and it worked perfectly.

## Issues and Suggestions

I am open to any kind of suggestion and will try to solve issues as soon as possible. Still it may take a while until I actually find a solution or I manage to add a certain feature. You have my full consent to just fork the repository and fix it yourself.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](https://github.com/magnuschase293/comic_getter/blob/master/LICENSE) file for details

## Donations

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/magnuschase293)
