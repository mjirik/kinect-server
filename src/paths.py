import sys
import os

BASE_DIR = os.path.dirname(__file__)

def setup():
    pos = 0
    for path in [["."]]:
        path = os.path.abspath(os.path.join(*([BASE_DIR] + path)))
        if os.path.isdir(path) and (path not in sys.path):
            sys.path.insert(pos, path)
            pos += 1
