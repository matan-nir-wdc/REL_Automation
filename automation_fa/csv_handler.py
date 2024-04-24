import pandas as pd


def get_data(file, sep=',', names="", encoding='latin-1', low_memory=False, skiprows=0, fix_header=True):
    if names:
        df = pd.read_csv(filepath_or_buffer=file, sep=sep, names=names, encoding=encoding, low_memory=low_memory,
                        skiprows=skiprows)
    else:
        df = pd.read_csv(filepath_or_buffer=file, sep=sep, encoding=encoding, low_memory=low_memory, skiprows=skiprows)
    if fix_header:
        df.columns = df.columns.str.replace(' ', '')
    return df


def check_value_exist(data, value):
    '''Need Work'''
    return 0


def return_all_found_events(data, header, value, compare="=="):
    try:
        if compare == "==":
            data = data[data[f'{header}'] == value]
        elif compare == ">":
            data = data[data[f'{header}'] > value]
        elif compare == "<":
            data = data[data[f'{header}'] < value]
        elif compare == "str":
            value = value.lower()
            data = data[data[f'{header}'].str.lower().str.contains(f'{value}')]
    except TypeError as e:
        print(e)
        if compare == "==":
            data = data[data[f'{header}'] == str(value)]
        elif compare == ">":
            data = data[data[f'{header}'] > str(value)]
        elif compare == "<":
            data = data[data[f'{header}'] < str(value)]
        elif compare == "str":
            data = data[data[f'{header}'].str.lower().str.contains(f'{value}')]
    return data


def return_signle_event(data, header, value, is_numeric=False):
    if is_numeric:
        return data[data[f'{header}'] == value]
    return data[data[f'{header}'].str.lower().str.contains(f'{value}')]


def reduce_header(data, headers):
    return data[headers]


def combine_data(data1, data2):
    frames = [data1, data2]
    return pd.concat(frames)


def get_amount_per_colum(data, header, value):
    return data[f'{header}'].str.contains(f"{value}").sum()


def get_index_by_value(data, header, value):
    res = data[data[f'{header}'].str.contains(f'{value}')].index
    return res.to_list()
