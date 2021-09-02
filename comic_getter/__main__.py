import os
import comic_getter

if __name__=="__main__":
    main_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(main_dir, "comic_getter.py")
    exec(open(f"{filepath}").read())
