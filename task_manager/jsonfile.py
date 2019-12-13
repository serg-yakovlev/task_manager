import json

with open('proc_list_json', 'r') as file:
    processes = json.loads(file.read())
print(processes)