import json


def get_data(file):
    with open(file, mode='r', encoding='utf-8') as data:
        data = data.readlines()
    return data

def get_json_data(file):
    with open(file, mode='r', encoding='utf-8') as data:
        data = data.read()
        data = json.loads(data)
    return data

