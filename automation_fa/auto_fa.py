import os
import zipfile
from argparse import ArgumentParser

import project as PRJ
import FileHandler as FH
import vtf_handler as VTF
import emonitor as EMonitor
import ProtocolLog as PL
import smartReport as SR
import ctf_handler as CTF


def vtf_info(path):
    FH.print_head_line("VTF Log")
    vtf_log = VTF.vtf_event2_info(path)
    rel_err = VTF.get_rel_from_data(path=path)
    vtf_log.update(rel_err)
    FH.write_file(folder_path=path, section_name="VTF Log:", report=vtf_log)
    return vtf_log


def protoco_log_info(path, vtf):
    FH.print_head_line("protocol Log")
    res = PL.get_timestamp_event(path, vtf)
    if res:
        FH.write_file(folder_path=path, section_name="Protocol log:", report=res)


def ctf_log_error(path, full_ctf_cmd, vtf_data):
    FH.print_head_line("CTF Log")
    CTF.get_ctf_data(path=path, full_ctf_cmd=full_ctf_cmd, vtf_data=vtf_data)


def smartReport(main_folder, project_json):
    FH.print_head_line("Smart Report")
    SR.get_smart_report(main_folder, project_json=project_json)


def emonitor_actions(path):
    FH.print_head_line("RWR Fast Scan")
    rwr_files, rwr_issues = EMonitor.run_emonitor(path)
    if rwr_files:
        FH.write_file(folder_path=path, section_name="RWR_Files:", report=rwr_files)
        FH.write_file(folder_path=path, section_name="RWR_issue:", report=rwr_issues)


def create_folder(path):
    try:
        os.makedirs(path)
        print(f"Folder created at {path}")
    except FileExistsError:
        print(f"Folder already exists at {path}")


def get_zip_file_list(path):
    zip_files = []
    for file in os.listdir(path):
        if file.endswith(".zip"):
            zip_files.append(file)
    return zip_files


def unzip_file(zip_file, extract_folder):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)


def run_auto_fa(args, path):
    vtf_data = vtf_info(path)
    ctf_log_error(path, args.full_ctf, vtf_data)
    smartReport(path, project_json=current_project.smartReport)
    emonitor_actions(path)
    protoco_log_info(path, vtf_data)
    FH.remove_quotes_from_file(path)



if __name__ == "__main__":
    parser = ArgumentParser(description='Automation FA.', epilog='REL Team FA Automation')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--path', type=str, help='path to result folder.')
    group.add_argument('--zip_path', type=str, help='path to zips folder.')
    parser.add_argument('--full_ctf', action='store_true')
    parser.add_argument('--full_vtf', action='store_true')
    parser.add_argument('--zip_file', action='store_true', help="is the folder zipped")
    parser.add_argument('--project', type=str, choices=['SPA', 'OBERON'], required=True)
    args = parser.parse_args()
    current_project = PRJ.choose(args.project)
    if args.zip_path:
        zip_list = get_zip_file_list(args.zip_path)
        for zip in zip_list:
            name = f"{zip.split('.zip')[0]}"
            zip_folder = f"{args.zip_path}\\{zip.split('.zip')[0]}"
            zip = f"{args.zip_path}\\{zip}"
            create_folder(zip_folder)
            unzip_file(zip, zip_folder)
            print(f"done unziping {zip}")
            run_auto_fa(args, zip_folder)
            FH.copy_res(main_folder=args.zip_path, path=zip_folder, name=name)
    else:
        run_auto_fa(args, args.path)
    print("Done Auto FA.")
