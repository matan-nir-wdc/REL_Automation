import csv
import glob
import pathlib
import re
import subprocess
import sys

import FileHandler as FH
import os.path
from info_dictionary import rwr, rwr_files


def run_emonitor(path="C:\\temp"):

    print("Getting eMonitor folder.")
    emonitor = "C:\\Program Files (x86)\\Default Company Name\\eMonitorSetup\\eMonitor.exe"
    if not os.path.exists(emonitor):
        print(f"No eMonitor MST version found.")
        return None
    files = FH.getFilesPath(path=path, exception="rwr")
    decrypt_path = FH.getFilePath(original_file_path=path, file_name="*decrypt.bot")
    print()
    print("Start reading RWR file.")
    rwr_numbers = []
    for rwr in files:
        num_of_rwr = re.search('\d+', rwr).group()
        rwr_numbers.append(num_of_rwr)
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
    FH.print_head_line(file_name="RWR")
    count = {}
    rwr_files_tmp = rwr_files
    print("Checking RWR results, may take up to 3 minutes.")
    for file_number in rwr_numbers:
        save_file = f"{path}\\temp{file_number}.csv"
        with open(f'{save_file}', mode='r') as data:
            csvFile = csv.DictReader(data)
            for row in csvFile:
                event = row["name"].split("{")[0]
                add_to_file = ("assert", "UECC", "fatal", "assert", "GBB")
                for files in add_to_file:
                    if files in event:
                       rwr_files_tmp[f'{files}_files'].append(file_number)
                       rwr_files_tmp[f'{files}_files'] = list(dict.fromkeys(rwr_files_tmp[f'{files}_files']))
                if row['name'] in count.keys():
                    count[f'{row["name"]}'] = count[f'{row["name"]}'] + 1
                else:
                    count[f'{row["name"]}'] = 1
    for file in rwr_numbers:
        file_to_rem = pathlib.Path(f"{path}\\temp{file}.csv")
        file_to_rem.unlink()
    FH.write_file(folder_path=path, section_name="RWR_Files:", report=rwr_files_tmp)
    return count


def check_known_errors(results):
    check = rwr
    for key in check:
        sum = 0
        for value in results:
            tmp_value = value.split("(")[0].lower()
            if key in tmp_value:
                check[f'{key}'].append(value)
                sum = sum + results[f'{value}']
        check[f'{key}'].append(sum)
    return check
