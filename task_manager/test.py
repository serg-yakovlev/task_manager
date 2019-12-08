import re
import os


string = '/usr/bin/python3.6'
path = os.path.split(string)
print(path[1])