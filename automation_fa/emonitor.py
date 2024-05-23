import re
import subprocess
import sys

import FileHandler as FH
import os.path
import csv_handler as CSV
from info_dictionary import rwr, rwr_files
from ast import literal_eval


def contains_number(strings):
    for string in strings:
        if not any(char.isdigit() for char in string):
            return True
    return False


def get_fw_version_from_device(data, path):
    fw = CSV.return_signle_event(data=data, header="name", value="whoami")
    ver = []
    fw = fw['parameters'].str.split("|").to_list()
    try:
        ver.append(int(fw[0][0][2:]))
        ver.append(int(fw[0][1][2:]))
        ver.append(int(fw[0][2], 16))
        ver = str(ver[0]) + str(ver[1]) + "." + str(ver[2])
        FH.write_file(folder_path=path, section_name=f"FW Version", report=ver)
        print(ver)
    except IndexError as e:
        print(e)


def check_for_dme_issue(data, path):
    print("Checking for DME issue")
    dme_val_20_issue(data, path)
    DME_NAC_issue(data, path)
    print("Done checking for DME issue.")


def dme_val_20_issue(data, path):
    event = "MPHY ISR PMI"
    val = "20"
    issue = CSV.return_all_found_events(data=data, header='name', value=event, compare="str")
    new_df = issue['parameters'].str.endswith(f'{val}').to_frame()
    index = new_df.index[new_df['parameters'] == True].tolist()
    if len(index) > 0:
        dme = issue.loc[[index[0]]].to_string()
        FH.write_file(folder_path=path,
                      section_name=f"Found DME issue(Add 'PMI x020' to FAR, amount={len(index)}):", report=dme)
        print("Found PMI 0x20 issue.")
        return
    del index
    print("No PMI 0x20 issue found.")


def DME_NAC_issue(data, path):
    event = "lane0_falling"
    issue = CSV.return_all_found_events(data=data, header='name', value=event, compare="str")
    print(f"Found {len(issue)} Lane0_Falling")
    if len(issue) > 999:
        df = issue.iloc[0].to_string(index=False)
        FH.write_file(folder_path=path,
                      section_name=f"Found DME issue(Add Lane0_Falling to FAR), amount={len(df)}:", report="")
        print("Found Lane0_Falling issue.")
        return
    event = "nac_received"
    issue = CSV.return_all_found_events(data=data, header='name', value=event, compare="str")
    print(f"Found {len(issue)} NAC_RECEIVED")
    if len(issue) > 199:
        df = issue.iloc[0].to_string(index=False)
        FH.write_file(folder_path=path,
                      section_name=f"Found DME issue(Add NAC_RECIEVED to FAR), amount={len(df)}:", report=df)
        print("Found NAC_RECIEVED issue.")


def get_prog_fail(data, path):
    value = "progFail: PS: EH  PF STATE(PFstate)"
    issue = CSV.return_all_found_events(data=data, header='name', value=value, compare="str")
    if len(issue) > 0:
        print("Found progFail")
        FH.write_file(folder_path=path, section_name=f"Found progFail:", report=issue, file_name="tmp.txt")
        FH.combine_files(first_file_path=f"{path}\\tmp.txt", sec_file_path=f"{path}\\REL_result.txt")


def get_assert_file(original_data, data, path):
    index = CSV.get_index_by_value(data=data, header="issue1", value="System exception pt1")
    if len(index) > 0:
        assert_issue = original_data.loc[[index[0]]]
        assert_file_line = assert_issue['parameters']
        assert_file_line = assert_file_line.to_string().split("|")[1:3]
        file = literal_eval(assert_file_line[0])
        line = literal_eval(assert_file_line[1])
        source = assert_issue['source'].to_string()
        issue_in = "file19.txt" if "PS" in source else "file18.txt"
        report = f'"FOUND ASSERT ISSUE!!!" \nAssert in file: {issue_in}, row to file: {file}, line in file: {line}'
        FH.write_file(folder_path=path, section_name="Found assert issue", report=report)
        print("FOUND ASSERT ISSUE!!!")
        FH.write_file(folder_path=path, section_name="Found assert issue", report=report, file_name="tmp.txt")
        FH.combine_files(first_file_path=f"{path}\\tmp.txt", sec_file_path=f"{path}\\REL_result.txt")
    else:
        print("No assert issues found.")


def run_emonitor(path="F:\\AutoFA", amount_of_rwr=2):
    print("Getting eMonitor folder.")
    emonitor = "C:\\Program Files (x86)\\Default Company Name\\eMonitorSetup\\eMonitor.exe"
    if not os.path.exists(emonitor):
        print(f"No eMonitor MST version found.")
        return None
    decrypt_path = FH.getFilePath(original_file_path=path, file_name="*decrypt.bot")
    files = FH.getFilesPath(path=path, exception="rwr")
    tmp_files = []
    for file in files:
        file = file.split("\\")[-1]
        tmp_files.append(file)
    files = tmp_files
    del tmp_files
    print("Start reading RWR file.")
    check_rwr = True
    rwr_number = []
    for string in files:
        rwr_number.extend([int(x) for x in re.findall(r'\d+', string)])
    rwr_number = sorted(rwr_number)
    if len(files) == 0:
        check_rwr = False
    elif "ATB_LOG.rwr" in files and len(files) < 3:
        rwr_files = files
        rwr_number = rwr_number.appent("0")
    else:
        rwr_files = files[((-1)*(amount_of_rwr)):]
        rwr_number = rwr_number[((-1)*(amount_of_rwr)):]
    if check_rwr:
        num = 0
        read_files = []
        for file in rwr_files:
            save_file = f"{path}\\temp_{rwr_number[num]}.csv"
            read_files.append(save_file)
            # rwr_cmd = f'"{emonitor}" -l -n1 "{decrypt_path}" "{path}\\{rwr}" "{save_file}"'
            num_of_rwr = "" if rwr_number[num] == "0" else rwr_number[num]
            rwr_cmd = f'"{emonitor}" -l -n1 "{decrypt_path}" "{path}\\ATB_LOG_{num_of_rwr}.rwr" "{save_file}"'
            print(rwr_cmd)
            p = subprocess.Popen(rwr_cmd, stdout=subprocess.PIPE, bufsize=3)
            out = p.stdout.read(1)
            while out != b'':
                sys.stdout.write(out.decode("utf-8"))
                sys.stdout.flush()
                out = p.stdout.read(1)
            print("Done Reading 1 RWR file.")
            num = num + 1
        return read_results(rwr_numbers=rwr_number, result_path=path, results_files=read_files)
    return None, None


def read_results(rwr_numbers, result_path, results_files):
    FH.print_head_line(file_name="RWR")
    rwr_files_tmp = rwr_files.copy()
    rwr_issues = rwr.copy()
    get_fw = True
    amount_of_issue = rwr.copy()
    for key in amount_of_issue:
        amount_of_issue[key] = 0
    print("Checking RWR results.")
    for i, save_file in enumerate(results_files):
        data = CSV.get_data(file=save_file, encoding='utf-8', fix_header=False)
        print("Done reading the results.")
        if get_fw:
            print("Getting FW version from device")
            get_fw_version_from_device(data=data, path=result_path)
            get_fw = False
        check_for_dme_issue(data=data, path=result_path)
        get_prog_fail(data=data, path=result_path)
        print('Start analysis:')
        new_df = data['name'].str.split('(', expand=True)
        new_df.columns = ['issue{}'.format(x + 1) for x in new_df.columns]
        for search in rwr.keys():
            print(f"Checking for {search} in the results.")
            issue = CSV.return_all_found_events(data=new_df, header='issue1', value=search, compare="str")
            amount = CSV.get_amount_per_colum(data=issue, header='issue1', value=search)
            if search == "exception":
                print("Checking for assert issue:")
                get_assert_file(original_data=data, data=issue, path=result_path)
            if amount > 0:
                if search in ["assert", "fatal", "uecc", "gbb", "err"]:
                    rwr_files_tmp[f'{search}_files'].append(rwr_numbers[i])
                combined_series_cat = issue['issue1'].str.cat(issue['issue2'], sep='(')
                del issue
                issue = combined_series_cat.tolist()
                amount_of_issue[f'{search}'] = amount_of_issue[f'{search}'] + amount
                rwr_issues[f'{search}'] = rwr_issues[f'{search}'] + issue
        FH.remove_file(file=f"{save_file}")
    for search in rwr.keys():
        rwr_issues[f'{search}'] = list(set(rwr_issues[f'{search}']))
        amount = amount_of_issue[f'{search}']
        rwr_issues[f'{search}'].append(f"amount = {amount}")
    return rwr_files_tmp, rwr_issues
