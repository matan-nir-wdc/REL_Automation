import csv
import os
from datetime import datetime
import json
import re
import FileHandler as FH


def create_file(path, project, fw):
    # Define the column names for the CSV
    columns = ['Cycle_id', 'ExecutionID', 'CardCapacity+Die', 'TestName', 'HostName', 'Adapter', 'Pass/Fail', 'Suspect',
               'DeviceCriticalFail', 'Path']
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d%m%Y")
    file_name = f"[{project}][{fw}]PO_report_{formatted_date}.csv"
    file_name_path = f"{path}\\{file_name}"
    if os.path.exists(file_name_path):
        return file_name_path
    # Create an empty CSV file with the given column names
    with open(file_name_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
    return file_name_path


def check_pass_failed(path):
    return FH.check_if_fail(path)


def add_data(data, file_path, zip_path):
    columns = ['Cycle_id', 'ExecutionID', 'CardCapacity+Die', 'TestName', 'HostName', 'Adapter', 'Pass/Fail', 'Suspect',
               'DeviceCriticalFail', 'Path']
    with open(f"{data}\\REL_results.txt", 'r') as file:
        content = file.read()
        json_block = re.search(r'\{.*?}', content, re.DOTALL)

        if json_block:
            json_str = json_block.group(0)
            json_data = json.loads(json_str)
            report_data = {'Cycle_id': json_data["cycleId"], 'ExecutionID': json_data["ExecutionId"],
                           'CardCapacity+Die': f"{json_data['card_capacity']}GBb+{json_data['die_count']}d",
                           'TestName': json_data["TestName"], 'HostName': json_data["HostName"],
                           'Adapter': json_data["Adapter"], 'Pass/Fail': check_pass_failed(str(data) + "\\VTFLog.log"),
                           'Suspect': "Will be added later", 'DeviceCriticalFail': "Will be added later",
                           'Path': zip_path}

        else:
            print("could not load")
            return

    with open(f"{file_path}", mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writerow(report_data)
    print("Data added to PO_report.csv")
