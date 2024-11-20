import re

import FileHandler as FH
from info_dictionary import vtf_log, vtf_asc, device_info
import logHandler as LOG


def get_device_info(path):
    device_info_tmp = device_info
    res = None
    try:
        with open(path, 'r') as data:
            lines = data.readlines()
        for line in lines:
            if "Device UID string" in line:
                tmp = line.split("string")
                device_info_tmp['UID'] = tmp[1].strip()
            elif "Test Name:"in line:
                tmp = line.split("\\")[-1].split(".")[0]
                device_info_tmp['TestName'] = tmp.strip()
            elif "HostName:" in line and not "SDR HostName:" in line:
                tmp = line.split(":")[1]
                device_info_tmp['HostName'] = tmp.strip()
            elif "SDR HostName:" in line:
                tmp = line.split(":")
                device_info_tmp['Adapter'] = tmp[1].strip()
            elif "ctf version" in line.lower():
                tmp = line.split(":")
                device_info_tmp['CTFVersion'] = tmp[1].strip()
            elif " ExecutionId:" in line:
                execution_id = re.search(r"ExecutionId:(\d+)", line)
                # If a match is found, extract the integer value
                execution_id_value = int(execution_id.group(1)) if execution_id else None
                device_info_tmp['ExecutionId'] = execution_id_value
            elif "description: {" in line:
                res = line
            elif "cycleId=" in line:
                tmp = line.split("=")
                cycle_id_match = re.search(r'\d+', tmp[1])
                if cycle_id_match:
                    device_info_tmp['cycleId'] = int(cycle_id_match.group())
            elif "Set Bus Mode to" in line:
                tmp = line.split(">>>")
                gear_match = re.search(r'\d+', tmp[1])
                if gear_match:
                    device_info_tmp['gear'] = int(gear_match.group())
                tmp = line.split("|")
                for value in tmp:
                    if "rate" in value:
                        device_info_tmp['rate'] = re.search(r'\d+', value).group()
                    if "lanes" in value:
                        device_info_tmp['lanes'] = re.search(r'\d+', value).group()
            elif "Elapsed time" in line:
                tmp = line.split("time")
                device_info_tmp['TTF'] = tmp[1].strip()

        if res:
            res_split = res.split("[")
            if len(res_split) >= 3:
                res_split_1 = res_split[1].split("]")[1].strip()
                res_split_2 = res_split[2].split("]")[1].strip()
                data_info = (res_split[0] + res_split_1 + res_split_2).split(",")
                for info in data_info:
                    for key in device_info_tmp.keys():
                        if key in info:
                            info_value = info.split(":")[1].strip()
                            if key == "type" and "flash_type" not in info:
                                device_info_tmp["type"] = info_value
                            elif key != "type":
                                device_info_tmp[key] = info_value
    except (ValueError, IndexError, AttributeError) as e:
        print(f"Error: {e}")
        return device_info_tmp
    return device_info_tmp


def vtf_event2_info(path):
    file_path = FH.getFilePath(original_file_path=path, file_name="VTFLog.log")
    device_info = get_device_info(file_path)
    even_2_data = FH.extract_event_from_file(file_path, "event 2")
    if even_2_data and device_info:
        device_info.update(extract_event2_data(even_2_data))
    elif even_2_data:
        return even_2_data
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
    if amount_of_lines < 1:
        return None
    values["asc"] = [s.lstrip() for s in line[start:end]]
    values["asc"] = [s.rstrip("\t\r\n") for s in values["asc"]]
    values["ascq"] = [s.lstrip() for s in line[start + amount_of_lines:end + amount_of_lines]]
    values["ascq"] = [s.rstrip("\t\r\n") for s in values["ascq"]]
    return values


def get_Command_UPIU(data):
    lines = data
    upiu = {"TaskTag": None}
    for line in lines:
        if "<Command UPIU>" in line:
            for value in lines:
                if "Task Tag =" in value:
                    value = value.translate({ord(i): None for i in '\n\r\t'})
                    upiu["TaskTag"] = value.split("Task Tag =")[1]
                    return upiu


def extract_event2_data(data):
    search = vtf_log
    for line in data:
        for key in search.keys():
            if key in line:
                res = line.split(key)[1]
                try:
                    val = int(re.search(r'\d+', res).group()) if key in ["UID", "Timestamp", "Lun"] else res[1:]
                except Exception as e:
                    val = "Not Found"
                    continue
                if isinstance(val, str):
                    val = val.translate({ord(i): None for i in '\n\r\t'})
                search[key] = val
    asc_ascq = get_asc_ascq(data)
    upiu = get_Command_UPIU(data)
    if asc_ascq:
        search.update(asc_ascq)
    if upiu:
        search.update(upiu)
    return search


def get_rel_from_data(path):
    file_path = FH.getFilePath(original_file_path=path, file_name="VTFLog.log")
    data = LOG.get_data(file_path)
    rel_err = {"REL Err in VTF": []}
    voltage = ""
    for line in data:
        if "rel err" in line.lower():
            rel_err["REL Err in VTF"].append(line.strip("\n"))
        elif "Current Voltage" in line:
            voltage = line
    rel_err["Voltage"] = voltage
    return rel_err


def get_test_name(path):
    try:
        file_path = FH.getFilePath(original_file_path=path, file_name="VTFLog.log")
        data = LOG.get_data(file_path)
        for line in data:
            if "Test=" in line:
                return line.split("\\")[-1]
    except Exception as e:
        print(e)
        return None
