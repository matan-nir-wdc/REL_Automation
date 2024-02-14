
def get_data(file):
    with open(file, mode='r', encoding='utf-8') as data:
        data = data.readlines()
    return data
