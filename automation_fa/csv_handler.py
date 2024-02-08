import pandas as pd


def get_data(file, encoding='utf-8', low_memory=False, skiprows=0):
    df = pd.read_csv(filepath_or_buffer=file, encoding=encoding, low_memory=low_memory, skiprows=skiprows)
    df.columns = df.columns.str.replace(' ', '')
    return df


def return_all_found_events(data, header, value):
    return 0
    pass


def return_fisrt_event(data, header, value):
    return data[data[f'{header}'] == value]


def return_last_event(data):
    res = return_all_found_events(data, header, value),
    return res.tail(1)
    pass


