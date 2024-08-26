import json
import FileHandler as FH


def get_pdl_file(path):
    folders = FH.get_all_folders_in_path(path)
    file_path = ""
    for folder in folders:
        file_path = FH.getFilePath(original_file_path=folder, file_name="PDL*.json")
        if file_path:
            return file_path
    if not file_path:
        print("Need to check manually")
        return None



def get_gear_info(data):
    gear_info = []
    gear_change = {"PmcByHostCount": 0, "PmcByDeviceCount": 0}
    device_rx_error = {"PaLane0ErrCount": 0, "PaLane1ErrCount": 0, "DlCrcErrCount": 0, "DlFrameErrCount": 0}
    logical_error = {"PaLineResetErrCount": 0, "DlTcxRplyTimrExpRcvErrCount": 0, "DlAfcxReqstTimrExpErrCount": 0,
                    "DlFcxProtectionTimrExpErrCount": 0}
    for i, gear_data in enumerate(data):
        tmp_gear_data = gear_data.copy()
        for key in gear_change.keys():
            try:
                del gear_data[key]
            except KeyError as e:
                pass
        if all(value == 0 for value in gear_data.values()):
            continue
        gear_info.append("-" * 30)
        gear_info.append(f"Gear {i+1}:")
        gear_info.append("-" * 30)
        gear_info.append("[Gear change]")
        for key in tmp_gear_data.keys():
            gear_info.append(f"{key} :{tmp_gear_data[key]}")
        gear_info.append("")
        gear_info.append("[Device RX Error]")
        for key in device_rx_error.keys():
            gear_info.append(f"{key} :{gear_data[key]}")
        gear_info.append("")
        gear_info.append("[SDR RX Error]")
        gear_info.append(f'DlNacRcvErrCount :{gear_data["DlNacRcvErrCount"]}')
        gear_info.append("")
        gear_info.append("[Logical Error]")
        for key in logical_error.keys():
            gear_info.append(f"{key} :{gear_data[key]}")
        gear_info.append("")
        gear_info.append("[Fatal Error]")
        gear_info.append(f'PaInitErrorCount :{gear_data["PaInitErrorCount"]}')
        gear_info.append("")
    return gear_info


def check_for_err_fail(pdl_file):
    with open(pdl_file, 'r') as file:
        data = json.load(file)
        pdl_print = {}
    pdl_data = FH.get_all_keys(nested_dict=data)
    gear_info = pdl_data["Gearcounters"]
    del pdl_data["Gearcounters"]
    for key in pdl_data:
        if "Error" in key or "Failure" in key:
            if pdl_data[key] > 0:
                pdl_print[key] = pdl_data[key]
    gear_data = get_gear_info(gear_info)
    return pdl_print, gear_data
