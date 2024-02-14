import csv_handler as CSV
import FileHandler as FH


def get_timestamp_event(path, vtf, show_cmd=5):
    folder = FH.getFilePath(path, file_name="PROTOCOL_LOG")
    if len(folder) < 1:
        print("Searching for protocolLog*.csv")
        protocol_file = FH.getFilePath(path, file_name="protocolLog*.csv")
    else:
        files = FH.getFilesPath(path=folder, exception="csv")
        protocol_file = files[-1]
    res = search_cmd_timestamp(protocol_file, vtf, show_cmd)
    return res


def search_cmd_timestamp(file, vtf, show_cmd):
    data = CSV.get_data(file=file, skiprows=20)
    headers_needed = ['Timestamp', 'Time', 'TypeofPacket', 'TransactionType', 'IID', 'TASKTag', 'LUN', 'Data']
    res = CSV.reduce_header(data=data, headers=headers_needed)
    res = CSV.return_signle_event(data=res, header='Timestamp', value=vtf['Timestamp'])
    if len(res.index) == 1:
        return res
    else:
        res1 = CSV.return_all_found_events(data=data, header='Timestamp', value=vtf['Timestamp'], compare="<")
        res2 = CSV.return_all_found_events(data=data, header='Timestamp', value=vtf['Timestamp'], compare=">")
        res = CSV.combine_data(res1.tail(show_cmd), res2.head(show_cmd))
        return f"No Time Stamp found, Here is {show_cmd} before and after : \n" + res.to_string()
