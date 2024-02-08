import csv
import pandas as pd

import FileHandler as FH


def get_timestamp_event(path, vtf, show_cmd=5):
    folder = FH.getFilePath(path, file_name="PROTOCOL_LOG")
    files = FH.getFilesPath(path=folder, exception="csv")
    protocol_file = files[-1]
    res = extract_from_protocol_log(protocol_file, vtf, show_cmd)
    return res


def extract_from_protocol_log(file, vtf, show_cmd):
    res = search_cmd_timestamp(file=file, time_stamp=vtf['Timestamp'], show_cmd=show_cmd)
    result = res[['Timestamp', ' Time ', 'Type of Packet', 'Transaction Type', 'IID ', 'TASK Tag', ' LUN',
                  'Data']].to_string()
    if len(result.splitlines()) > 2:
        result = f"No Time Stamp found, Here is {show_cmd} before and after : \n" + result
    return result


def search_cmd_timestamp(file, time_stamp, show_cmd=5):
    time_stamp = 1005
    df = pd.read_csv(f'{file}', encoding='utf-8', low_memory=False, skiprows=20)
    found = df[df["Timestamp"] == time_stamp]
    if len(found['Timestamp']) == 1:
        uid = found['TASK Tag'][1]
        res = df[(df['TASK Tag'] == uid) & (df['Transaction Type'] == "RESPONSE")].head(1)
    else:
        pre = df[df["Timestamp"] < time_stamp].tail(show_cmd)
        post = df[df["Timestamp"] > time_stamp].tail(show_cmd)
        frames = [pre, post]
        res = pd.concat(frames)
    return res
