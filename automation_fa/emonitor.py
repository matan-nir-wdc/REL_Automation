import os
import re
import subprocess
import sys
import FileHandler as FH
import csv_handler as CSV
import pandas as pd
from ast import literal_eval
from info_dictionary import rwr
from typing import List, Union


def get_emonitor_path() -> Union[str, None]:
    emonitor = "C:\\Program Files (x86)\\Default Company Name\\eMonitorSetup\\eMonitor.exe"
    return emonitor if os.path.exists(emonitor) else None


def process_files(files: List[str]) -> str:
    rwr_number = sorted([int(x) for x in re.findall(r'\d+', ' '.join(files))])
    if "ATB_LOG.rwr" in files:
        return "ATB_LOG.rwr"
    else:
        return f"ATB_LOG_{rwr_number[0]}.rwr"


def run_emonitor(path: str = "F:\\AutoFA", sres: bool = False):
    emonitor = get_emonitor_path()
    if not emonitor:
        print("No eMonitor MST version found.")
        return None

    decrypt_path = FH.getFilePath(original_file_path=path, file_name="*decrypt.bot")
    files = FH.getFilesPath(path=path, exception="rwr")

    if len(files) == 1 and os.path.getsize(files[0]) < 1000000:
        print("Too Small RWR")
        FH.write_file(folder_path=path, section_name="RWR Under 1M", report="")
        return None, None

    files = [file.split("\\")[-1] for file in files]
    rwr_file = process_files(files)

    if rwr_file:
        if read_rwr_files(emonitor, decrypt_path, path, rwr_file):
            return read_results(result_path=path, check_error=files)
    print("Could not read RWR files, please check")
    return None


def read_results(result_path: str, check_error: [str]) -> dict:
    FH.print_head_line(file_name="RWR")
    rwr_issues = rwr.copy()
    amount_of_issue = {key: 0 for key in rwr}
    print("Checking RWR results.")
    data = CSV.get_data(file=f"{result_path}\\FAST_SCAN.csv", encoding='utf-8', fix_header=False)
    data = data.loc[:, ~data.columns.str.contains('%')]
    name = "amount"
    data = data.rename(columns={data.columns[3]: name})
    print("Done reading the results.")
    analyze_data(path=result_path, data=data, rwr_issues=rwr_issues, amount_of_issue=amount_of_issue)
    check_sign(path=result_path)
    if any(amount_of_issue[issue] > 0 for issue in ["assert", "fatal", "exception", "uecc"]):
        if amount_of_issue["exception"] > 1:
            for val in rwr_issues["exception"]:
                if "System exception pt1" in val:
                    get_assert_file(data=data, path=result_path, check_error=check_error)
    for search in rwr.keys():
        rwr_issues[search].append(f"amount = {amount_of_issue[search]}")
    compare_process(data, path=result_path)
    check_for_value_issue(data, path=result_path, check_error=check_error)
    return rwr_issues


def analyze_data(path, data, rwr_issues, amount_of_issue):
    keywords = rwr.keys()
    print("Checking the result")
    for row in data.itertuples(index=True, name='Pandas'):
        # Split the name by '(' and take the first part
        first_part = row.name.split('(')[0].strip()
        # Check if the first part contains any of the keywords
        for key in keywords:
            if key in str(first_part).lower():
                rwr_issues[key].append(f"[{row.name}], amount: {row.amount}")
                amount_of_issue[key] = amount_of_issue[key] + int(row.amount)


def check_sign(path):
    issue_apear_more_than_standart = []
    # Load the Excel file
    # Specify the path to the Excel and CSV files
    excel_file = "automation_fa/issue_by_amount.xlsx"
    csv_file = f"{path}/FAST_SCAN.csv"  # Adjust 'path' as needed

    # Load the Excel file
    issue_sign = pd.read_excel(excel_file)
    # Load the CSV file
    csv_df = pd.read_csv(csv_file)

    # Rename the 4th column (column D) to 'amount'
    csv_df.rename(columns={csv_df.columns[3]: 'amount'}, inplace=True)

    # Save the modified DataFrame back to the CSV file
    csv_df.to_csv(csv_file, index=False)

    # Iterate over each value in the 'name' column of the Excel file
    for index, row in issue_sign.iterrows():
        excel_name = row['name'].lower()
        amount_need = row['amount']

        # Check if the Excel name is contained in any of the CSV names
        for _, csv_row in csv_df.iterrows():
            csv_name = csv_row['name'].lower()
            amount_found = csv_row['amount']

            if excel_name in csv_name and amount_found >= amount_need:
                issue_apear_more_than_standart.append(f"[{excel_name}], amount: " + str(amount_found))
    FH.write_file(folder_path=path, section_name="Issues that appear more than approved:\n",
                  report=issue_apear_more_than_standart)
    print("finish check_sign")


def read_rwr_files(emonitor: str, decrypt_path: str, path: str, rwr_file: str) -> bool:
    save_file = f"{path}\\FAST_SCAN.csv"
    rwr_cmd = f'"{emonitor}" -s "{decrypt_path}" "{path}\\{rwr_file}" "{save_file}"'
    print(rwr_cmd)
    try:
        run_subprocess(rwr_cmd)
        print("Done Reading All RWR files.")
        return True
    except Exception as e:
        print(e)
        return False


def run_subprocess(command: str):
    with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=3) as p:
        for out in iter(lambda: p.stdout.read(1), b''):
            sys.stdout.write(out.decode("utf-8"))
            sys.stdout.flush()


def compare_process(data, path):
    print("Checking for unfinished process")
    start = CSV.return_all_found_events(data=data, header='name', value='Process begin', compare='str')
    end = CSV.return_all_found_events(data=data, header='name', value='Process end', compare='str')
    # Extract the part of 'name' before '['
    df1 = start.assign(split_name=start['name'].str.split('[').str[0])
    df2 = end.assign(split_name=end['name'].str.split('[').str[0])
    results = []
    # Iterate through each row in df1
    for _, row1 in df1.iterrows():
        # Find the corresponding row in df2
        matching_row = df2[df2['split_name'] == row1['split_name']]
        if not matching_row.empty:
            row2 = matching_row.iloc[0]
            # Compare the 'amount' values
            if row1['amount'] > row2['amount']:
                # Store the full name from df1 and the amount
                results.append((row1['name'], row1['amount']))
                results.append((row2['name'], row2['amount']))
    FH.write_file(folder_path=path, section_name="Unfinished process:", report=results)
    print("Finish checking for unfinished process")


def get_assert_file(data, path, check_error):
    res = CSV.return_all_found_events(data=data, header="name", value="System exception pt1", compare="str")
    if len(res) < 1:
        print("No assert issue found")
    if len(res) > 0:
        res = run_full_check(files=check_error, path=path, issue_name="assert", event="system exception pt1")
        print("Done reading RWR, checking the result")
        event = "system exception pt1"
        issue = CSV.return_all_found_events(data=res, header='name', value=event, compare="str")
        assert_file_line = res['parameters']
        assert_file_line = assert_file_line.to_string().split(",")[1:3]
        file = literal_eval(assert_file_line[0])
        line = literal_eval(assert_file_line[1])
        source = issue['source'].to_string()
        issue_in = "file19.txt" if "PS" in source else "file18.txt"
        report = f'"FOUND ASSERT ISSUE!!!" \nAssert in file: {issue_in}, row to file: {file}, line in file: {line}'
        FH.write_file(folder_path=path, section_name="Found assert issue", report=report)
        print("FOUND ASSERT ISSUE!!!")


def check_for_value_issue(data, path, check_error):
    check_error.reverse()
    print("Checking for Value issue")
    issue_apear = []
    value_needed = []
    found_issues = []
    excel_file = "automation_fa/issue_by_sign.xlsx"
    # Load the Excel file
    issue_sign = pd.read_excel(excel_file)
    # Load the CSV file
    # Iterate over each value in the 'name' column of the Excel file
    for index, row in issue_sign.iterrows():
        excel_name = row['name'].lower()
        value = row['value']

        # Check if the Excel name is contained in any of the CSV names
        for _, data_check in data.iterrows():
            csv_name = data_check['name'].lower()

            if excel_name in csv_name:
                issue_apear.append(excel_name)
                value_needed.append(value)

    for value, event in zip(value_needed, issue_apear):
        res = run_full_check(files=check_error, path=path, issue_name="check_sign", event=event)
        if not res.empty:
            new_df = res['parameters'].str.endswith(f'{value}').to_frame()
            is_found = new_df.index[new_df['parameters'] == True].tolist()
            if any(is_found):
                found_issues.append(res.to_string())
        FH.write_file(folder_path=path, section_name=f"Found issue by sign:", report=found_issues)


def run_full_check(files, path, issue_name, event):
    emonitor = "C:\\Program Files (x86)\\Default Company Name\\eMonitorSetup\\eMonitor.exe"
    save_file = f"{path}\\{issue_name}.csv"
    check_file = f"{path}\\check.csv"
    decrypt_path = FH.getFilePath(original_file_path=path, file_name="*decrypt.bot")
    df = "0"
    for file in files:
        rwr_cmd = f'"{emonitor}" -s -n1 "{decrypt_path}" "{path}\\{file}" "{save_file}"'
        print(rwr_cmd)
        run_subprocess(rwr_cmd)
        print("Done reading 1 RWR file, now searching")
        res = CSV.get_data(file=f"{save_file}")
        filtered_df = res[res['name'].str.lower().str.contains(event)]
        if len(filtered_df) > 0:
            print("reading 1 RWR file")
            rwr_cmd = f'"{emonitor}" -t -n1 "{decrypt_path}" "{path}\\{file}" "{check_file}"'
            run_subprocess(rwr_cmd)
            print("Filtering 1 RWR file")
            res = CSV.get_data(file=f"{check_file}")
            filtered_df = res[res['name'].str.lower().str.contains(event)]
            return filtered_df
    return None


def get_fw_version_from_device(data, path):
    fw = CSV.return_signle_event(data=data, header="name", value="whoami")
    ver = []
    fw = fw['parameters'].to_list()
    fw = fw[0].split(",")
    try:
        str1 = fw[0][2:]
        str2 = fw[1][2:]
        ver.append(int(str1, 10))
        ver.append(int(str2, 10))
        ver.append(int(fw[2], 16))
        ver = f"{str(ver[0])}{str(ver[1])}.{str(ver[2])}"
        FH.write_file(folder_path=path, section_name=f"FW Version", report=ver)
        print(ver)
    except IndexError as e:
        print(e)
        pass
