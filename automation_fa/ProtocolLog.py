import csv_handler as CSV
import FileHandler as FH


def get_timestamp_event(path, vtf, show_cmd=5):
    folder = FH.getFilePath(path, file_name="PROTOCOL_LOG")
    if len(folder) < 1:
        print("searching for protocol*.csv")
        protocol_file = FH.getFilePath(path, file_name="protocol*.csv")
    else:
        print("still checking")
        files = FH.getFilesPath(path=folder, exception="csv")
        protocol_file = files[-1]
    if protocol_file and vtf["Timestamp"]:
        res = search_cmd_timestamp(protocol_file, vtf, show_cmd)
    else:
        print("No Protocol Log found.")
        return None
    return res


def search_cmd_timestamp(file, vtf, show_cmd):
    if vtf['Timestamp'] == 'Not Found':
        return "Could Not find Time Stamp in VTF Log"
    data = CSV.get_data(file=file, skiprows=20)
    headers_needed = ['Timestamp', 'Time', 'TypeofPacket', 'TransactionType', 'IID', 'TASKTag', 'LUN', 'Data',
                      'ResetValue', 'DMEInd', 'DMEVector']
    res = CSV.reduce_header(data=data, headers=headers_needed)
    single = CSV.return_signle_event(data=res, header='Timestamp', value=vtf['Timestamp'], is_numeric=True)
    if len(single.index) == 1:
        return single.to_string()
    else:
        res1 = CSV.return_all_found_events(data=res, header='Timestamp', value=vtf['Timestamp'], compare="<")
        res2 = CSV.return_all_found_events(data=res, header='Timestamp', value=vtf['Timestamp'], compare=">")
        res = CSV.combine_data(res1.tail(show_cmd), res2.head(show_cmd))
        return f"No Time Stamp found, Here is {show_cmd} before and after : \n" + res.to_string()
