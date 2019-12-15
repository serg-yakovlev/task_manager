import json


with open('app_list_json', 'r') as file:
    string = file.read()
    print('rhythm' in string)