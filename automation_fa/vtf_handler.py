import FileHandler as FH
from info_dictionary import vtf_log, vtf_asc, device_info
import re


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
    except:
        print("error")
        # add gear
    return device_info_tmp


def vtf_event2_info(path):
    file_path = FH.getFilePath(original_file_path=path, file_name="VTFLog.log")
    device_info = get_device_info(file_path)
    even_2_data = FH.extract_event_from_file(file_path, "event 2")
    device_info.update(extract_event2_data(even_2_data))
    return device_info


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
    search.update(asc_ascq)
    return search
