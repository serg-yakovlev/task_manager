import json


with open('proc_list_json', 'r') as file:
    string = file.read()
    print('rhythm' in string)