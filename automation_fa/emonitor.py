import re
import subprocess
import sys

import FileHandler as FH
import os.path
import csv_handler as CSV
from info_dictionary import rwr, rwr_files


def check_for_dme_issue(data, path):
    print("Checking for DME issue")
    dme_val_20_issue(data, path)
    DME_NAC_issue(data, path)


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
        print("Found PMI x020 issue.")


def DME_NAC_issue(data, path):
    event = "Lane0_Falling"
    issue = CSV.return_all_found_events(data=data, header='name', value=event, compare="str")
    if len(issue) > 999:
        df = issue.iloc[0].to_string(index=False)
        FH.write_file(folder_path=path,
                      section_name=f"Found DME issue(Add Lane0_Falling to FAR), amount={len(df)}:", report="")
        print("Found Lane0_Falling issue.")
        return
    event = "NAC_RECEIVED"
    issue = CSV.return_all_found_events(data=data, header='name', value=event, compare="str")
    if len(issue) > 199:
        df = issue.iloc[0].to_string(index=False)
        FH.write_file(folder_path=path,
                      section_name=f"Found DME issue(Add NAC_RECIEVED to FAR), amount={len(df)}:", report=df)
        print("Found NAC_RECIEVED issue.")


def run_emonitor(path="C:\\temp"):
    print("Getting eMonitor folder.")
    emonitor = "C:\\Program Files (x86)\\Default Company Name\\eMonitorSetup\\eMonitor.exe"
    if not os.path.exists(emonitor):
        print(f"No eMonitor MST version found.")
        return None
    files = FH.getFilesPath(path=path, exception="rwr")
    tmp_files = []
    for file in files:
        file = file.split("\\")[-1]
        tmp_files.append(file)
    files = tmp_files
    decrypt_path = FH.getFilePath(original_file_path=path, file_name="*decrypt.bot")
    print("Start reading RWR file.")
    rwr_number = []
    pattern = re.compile(r'\d+')
    extracted_numbers = [pattern.findall(s) for s in files]
    for file in extracted_numbers:
        rwr_number = rwr_number + file
    for i in range(0, len(rwr_number)):
        rwr_number[i] = int(rwr_number[i])
    rwr_number = sorted(rwr_number)
    if len(rwr_number) < len(tmp_files) or len(tmp_files) == 1:
        rwr = "ATB_LOG.rwr"
        rwr_numer = 0
    else:
        rwr = rwr_number[-2]
        rwr_number = rwr
        for file in files:
            if str(rwr_number) in file:
                rwr = file
    save_file = f"{path}\\temp{rwr_number}.csv"
    # rwr_cmd = f'"{emonitor}" -l -n1 "{decrypt_path}" "{path}\\{rwr}" "{save_file}"'
    rwr_cmd = f'"{emonitor}" -l "{decrypt_path}" "{path}\\{rwr}" "{save_file}"'
    print(rwr_cmd)
    p = subprocess.Popen(rwr_cmd, stdout=subprocess.PIPE, bufsize=1)
    out = p.stdout.read(1)
    while out != b'':
        sys.stdout.write(out.decode("utf-8"))
        sys.stdout.flush()
        out = p.stdout.read(1)
    print("Done Reading RWR file.")
    return read_results(rwr_numbers=[rwr_number], result_path=path)


def read_results(rwr_numbers, result_path):
    FH.print_head_line(file_name="RWR")
    rwr_files_tmp = rwr_files
    rwr_issues = rwr
    print("Checking RWR results, may take up to 3 minutes.")
    for file_number in rwr_numbers:
        save_file = f"{result_path}\\temp{file_number}.csv"
        data = CSV.get_data(file=save_file, encoding='utf-8', fix_header=False)
        print("Done reading the results.")
        check_for_dme_issue(data=data, path=result_path)
        print('Start analysis:')
        new_df = data['name'].str.split('(', expand=True)
        new_df.columns = ['issue{}'.format(x + 1) for x in new_df.columns]
        for search in rwr.keys():
            issue = CSV.return_all_found_events(data=new_df, header='issue1', value=search, compare="str")
            amount = CSV.get_amount_per_colum(data=new_df, header='issue1', value=search)
            if amount > 0:
                if search in ["assert", "fatal", "UECC", "GBB", "err"]:
                    rwr_files_tmp[f'{search}_files'].append(file_number)
                issue = issue.drop_duplicates(subset=['issue1'])
                issue['com'] = issue['issue1'].astype(str) + "(" + issue['issue2']
                issue = issue['com'].values.tolist()
                issue.append(f"amount = {amount}")
                rwr_issues[f'{search}'] = issue
        for file in rwr_numbers:
            pass
            FH.remove_file(path=result_path, file=f"temp{file}.csv")
    return rwr_files_tmp, rwr_issues
