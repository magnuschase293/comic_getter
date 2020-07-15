import os
import comic_getter

def main():
    main_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(main_dir, "comic_getter.py")
    exec(open(filepath).read())
