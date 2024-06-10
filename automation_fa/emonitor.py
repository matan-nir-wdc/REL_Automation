import re
import subprocess
import sys

import FileHandler as FH
import os.path
import csv_handler as CSV
from info_dictionary import rwr, rwr_files
from ast import literal_eval
import pandas as pd



def contains_number(strings):
    for string in strings:
        if not any(char.isdigit() for char in string):
            return True
    return False


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


def check_for_dme_issue(path, all_files, main_issue):
    print("Checking for DME issue")
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)
    data = pd.concat(li, axis=0, ignore_index=True)
    main_issue = dme_val_20_issue(data, path, main_issue)
    DME_NAC_issue(data, path, main_issue)
    print("Done checking for DME issue.")


def dme_val_20_issue(data, path, main_issue):
    event = "MPHY ISR PMI"
    val = "20"
    issue = CSV.return_all_found_events(data=data, header='name', value=event, compare="str")
    new_df = issue['parameters'].str.endswith(f'{val}').to_frame()
    index = new_df.index[new_df['parameters'] == True].tolist()
    if len(index) > 0:
        dme = issue.loc[[index[0]]].to_string()
        with open(f"{path}\\REL_results.txt", 'r') as file:
            original_content = file.read()
            pmi_issue = ["-------------------------------------", "Only PMI found, FA logs clean",
                         "-------------------------------------"]
            pmi_issue = '\n'.join(pmi_issue)
            new_content = pmi_issue + "\n\n" + original_content if main_issue else original_content
            with open(f"{path}\\REL_results.txt", 'w') as file:
                file.write(new_content)
        FH.write_file(folder_path=path,
                      section_name=f"Found DME issue(Add 'PMI x020' to FAR, amount={len(index)}):", report=dme)
        print("Found PMI 0x20 issue.")
        return
    del index
    print("No PMI 0x20 issue found.")
    return True


def DME_NAC_issue(data, path, main_issue):
    event = "lane0_falling"
    issue = CSV.return_all_found_events(data=data, header='name', value=event, compare="str")
    print(f"Found {len(issue)} Lane0_Falling")
    if len(issue) > 500000:
        with open(f"{path}\\REL_results.txt", 'r') as file:
            original_content = file.read()
            lane0_falling_issue = ["-------------------------------------", "lane0_falling over 1K, FA logs clean",
                         "-------------------------------------"]
            lane0_falling_issue = '\n'.join(lane0_falling_issue)
            if main_issue:
                new_content = original_content
            else:
                new_content = lane0_falling_issue + "\n\n" + original_content
            with open(f"{path}\\REL_results.txt", 'w') as file:
                file.write(new_content)
        FH.write_file(folder_path=path,
                      section_name=f"Found DME issue(Add Lane0_Falling to FAR), amount={len(issue)}:", report="")
        print("Found Lane0_Falling issue.")
        return


def get_prog_fail(data, path):
    print("Search for prog fail")
    value = "ps: eh  pf state"
    issue = CSV.return_all_found_events(data=data, header='name', value=value, compare="str")
    if len(issue) > 0:
        print("Found progFail")
        issue = issue.to_string()
        with open(f"{path}\\REL_results.txt", 'r') as file:
            original_content = file.read()
            new_content = f"Found progFail:\n" + issue + original_content + "\n\n"
            with open(f"{path}\\REL_results.txt", 'w') as file:
                file.write(new_content)
                return False
    return True

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


def run_emonitor(path="F:\\AutoFA", amount_of_rwr=2, sres=False):
    print("Getting eMonitor folder.")
    emonitor = "C:\\Program Files (x86)\\Default Company Name\\eMonitorSetup\\eMonitor.exe"
    if not os.path.exists(emonitor):
        print(f"No eMonitor MST version found.")
        return None
    decrypt_path = FH.getFilePath(original_file_path=path, file_name="*decrypt.bot")
    files = FH.getFilesPath(path=path, exception="rwr")
    if len(files) == 1:
        if os.path.getsize(files[0]) < 1000000:
            print("Too Small RWR")
            FH.write_file(folder_path=path, section_name="RWR Under 1M", report="")

            return None, None
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
        rwr_number.append("0")
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
            num_of_rwr = "" if rwr_number[num] == "0" else "_" + str(rwr_number[num])
            rwr_cmd = f'"{emonitor}" -t -n1 "{decrypt_path}" "{path}\\ATB_LOG{num_of_rwr}.rwr" "{save_file}"'
            print(rwr_cmd)
            p = subprocess.Popen(rwr_cmd, stdout=subprocess.PIPE, bufsize=3)
            out = p.stdout.read(1)
            while out != b'':
                sys.stdout.write(out.decode("utf-8"))
                sys.stdout.flush()
                out = p.stdout.read(1)
            print("Done Reading 1 RWR file.")
            num = num + 1
        return read_results(rwr_numbers=rwr_number, result_path=path, results_files=read_files, sres=sres)
    return None, None


def read_results(rwr_numbers, result_path, results_files, sres):
    FH.print_head_line(file_name="RWR")
    rwr_files_tmp = rwr_files.copy()
    rwr_issues = rwr.copy()
    run_dme = True
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
            #get_fw_version_from_device(data=data, path=result_path)
            get_fw = False
        run_dme = get_prog_fail(data=data, path=result_path)
        if sres:
            run_dme = False
        print('Start analysis:')
        new_df = data['name'].str.split('(', expand=True)
        new_df.columns = ['issue{}'.format(x + 1) for x in new_df.columns]
        for search in rwr.keys():
            print(f"Checking for {search} in the results.")
            issue = CSV.return_all_found_events(data=new_df, header='issue1', value=search, compare="str")
            amount = len(issue)
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
        del data
    for search in ["assert", "fatal", "exception", "uecc"]:
        if int(amount_of_issue[f'{search}']) > 0:
            run_dme = False
            print(run_dme)
    for search in rwr.keys():
        rwr_issues[f'{search}'] = list(set(rwr_issues[f'{search}']))
        amount = amount_of_issue[f'{search}']
        rwr_issues[f'{search}'].append(f"amount = {amount}")
    check_for_dme_issue(path=result_path, all_files=results_files, main_issue=run_dme)
    for file in results_files:
        FH.remove_file(file=file)
    return rwr_files_tmp, rwr_issues
