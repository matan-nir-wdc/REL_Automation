import re
import subprocess
import sys

import FileHandler as FH
import os.path
import csv_handler as CSV
from info_dictionary import rwr, rwr_files


def run_emonitor(path="C:\\temp"):
    print("Getting eMonitor folder.")
    emonitor = "C:\\Program Files (x86)\\Default Company Name\\eMonitorSetup\\eMonitor.exe"
    if not os.path.exists(emonitor):
        print(f"No eMonitor MST version found.")
        return None
    files = FH.getFilesPath(path=path, exception="rwr")
    decrypt_path = FH.getFilePath(original_file_path=path, file_name="*decrypt.bot")
    print("Start reading RWR file.")
    rwr = files[-1]
    num_of_rwr = re.search('\d+', rwr).group()
    rwr_number = []
    save_file = f"{path}\\temp{num_of_rwr}.csv"
    rwr_cmd = f'"{emonitor}" -l -n1 "{decrypt_path}" "{rwr}" "{save_file}"'
    print(rwr_cmd)
    p = subprocess.Popen(rwr_cmd, stdout=subprocess.PIPE, bufsize=1)
    out = p.stdout.read(1)
    while out != b'':
        sys.stdout.write(out.decode("utf-8"))
        sys.stdout.flush()
        out = p.stdout.read(1)
    print("Done Reading RWR file.")
    return read_results(rwr_numbers=[num_of_rwr], result_path=path)


def read_results(rwr_numbers, result_path):
    FH.print_head_line(file_name="RWR")
    rwr_files_tmp = rwr_files
    rwr_issues = rwr
    print("Checking RWR results, may take up to 3 minutes.")
    for file_number in rwr_numbers:
        save_file = f"{result_path}\\temp{file_number}.csv"
        data = CSV.get_data(file=save_file, encoding='utf-8', fix_header=False)
        print("Done reading the results.")
        print('Start analysis:')
        new_df = data['name'].str.split('(', expand=True)
        new_df.columns = ['issue{}'.format(x + 1) for x in new_df.columns]
        for search in rwr.keys():
            issue = CSV.return_all_found_events(data=new_df, header='issue1', value=search, compare="str")
            amount = new_df['issue1'].str.contains(f"{search}").sum()
            if amount > 0:
                if search in ["assert", "fatal", "UECC", "GBB", "err"]:
                    rwr_files_tmp[f'{search}_files'].append(file_number)
                issue = issue.drop_duplicates(subset=['issue1']).to_string()
                rwr_issues[f'{search}'] = issue + f"\namount = {amount}"
        for file in rwr_numbers:
            FH.remove_file(path=result_path, file=f"temp{file}.csv")
        return rwr_files_tmp, rwr_issues
