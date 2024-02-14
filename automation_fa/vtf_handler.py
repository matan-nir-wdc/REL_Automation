import re

import FileHandler as FH
from info_dictionary import vtf_log, vtf_asc, device_info
import logHandler as LOG


def get_device_info(path):
    device_info_tmp = device_info
    try:
        with open(path, 'r') as data:
            lines = data.readlines()
        for line in lines:
            if "description: {" in line:
                lines = line
        lines = lines.split("[")
        lines[1] = lines[1].split("]")[1]
        lines[2] = lines[2].split("]")[1]
        data_info = (lines[0] + lines[1] + lines[2]).split(",")
        for info in data_info:
            for key in device_info_tmp.keys():
                if key in info:
                    if key == "type" and "flash_type" not in info:
                        device_info_tmp["type"] = info.split(":")[1]
                    elif key != "type":
                        device_info_tmp[key] = info.split(":")[1]
    except ValueError as e:
        print("error")
    except AttributeError as e:
        print(e)
        print("Pleases check VTF Log for changes")
        return None
    return device_info_tmp


def vtf_event2_info(path):
    file_path = FH.getFilePath(original_file_path=path, file_name="VTFLog.log")
    device_info = get_device_info(file_path)
    even_2_data = FH.extract_event_from_file(file_path, "event 2")
    if device_info:
        device_info.update(extract_event2_data(even_2_data))
        return device_info
    else:
        return extract_event2_data(even_2_data)



def get_asc_ascq(data):
    line = data
    values = vtf_asc
    start, end = 0, 0
    for i, string in enumerate(line):
        if "asc" in string.lower() and not "ascq" in string.lower():
            start = i
        if "ascq" in string.lower():
            end = i
    amount_of_lines = end - start
    if amount_of_lines < 1:
        return None
    values["asc"] = [s.lstrip() for s in line[start:end]]
    values["asc"] = [s.rstrip("\t\r\n") for s in values["asc"]]
    values["ascq"] = [s.lstrip() for s in line[start + amount_of_lines:end + amount_of_lines]]
    values["ascq"] = [s.rstrip("\t\r\n") for s in values["ascq"]]

    return values


def extract_event2_data(data):
    search = vtf_log
    for line in data:
        for key in search.keys():
            if key in line:
                res = line.split(key)[1]
                val = int(re.search(r'\d+', res).group()) if key in ["UID", "Timestamp", "Lun"] else res[1:]
                if isinstance(val, str):
                    val = val.translate({ord(i): None for i in '\n\r\t'})
                search[key] = val
    asc_ascq = get_asc_ascq(data)
    if asc_ascq:
        search.update(asc_ascq)
    return search


def get_rel_from_data(path):
    file_path = FH.getFilePath(original_file_path=path, file_name="VTFLog.log")
    data = LOG.get_data(file_path)
    rel_err = {"REL Err in VTF:": []}
    voltage = ""
    for line in data:
        if "REL Err" in line:
            rel_err["REL Err in VTF:"].append(line)
        elif "Current Voltage" in line:
            voltage = line
    rel_err["Voltage:"] = voltage
    return rel_err
