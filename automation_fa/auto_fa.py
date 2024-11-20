import os
from argparse import ArgumentParser
import project as PRJ
import FileHandler as FH
import vtf_handler as VTF
import emonitor as EMonitor
import ProtocolLog as PL
import smartReport as SR
import ctf_handler as CTF
import test_flow_handler as TFH
import pdl_handler as PDL


def pdl_report(path):
    FH.print_head_line("PDL")
    pdl = PDL.get_pdl_file(path)
    if pdl:
        pdl_res, gear_data = PDL.check_for_err_fail(pdl)
        if pdl_res:
            FH.write_file(folder_path=path, section_name="PDL:", report=pdl_res)
        if gear_data:
            FH.write_file(folder_path=path, section_name="PCU_HBA_COUNTERS:", report=gear_data)


def test_flow(path, project):
    TFH.get_test_flow(path=path, project=project)


def vtf_info(path):
    FH.print_head_line("VTF Log")
    vtf_log = VTF.vtf_event2_info(path)
    rel_err = VTF.get_rel_from_data(path=path)
    vtf_log.update(rel_err)
    FH.write_file(folder_path=path, section_name="VTF Log:", report=vtf_log)
    return vtf_log


def protocol_log_info(path, vtf):
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
    FH.write_file(folder_path=path, section_name="RWR_issue:", report="")
    rwr_issues = EMonitor.run_emonitor(path)
    if rwr_issues:
        FH.write_file(folder_path=path, section_name="", report=rwr_issues)


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


def run_auto_fa(path, project, remote=False):
    current_project = PRJ.choose(project)
    #test_flow(path=path, project=project)
    vtf_data = vtf_info(path)
    ctf_log_error(path, True, vtf_data)
    smartReport(path, project_json=current_project.smartReport)
    pdl_report(path)
    protocol_log_info(path, vtf_data)
    emonitor_actions(path)
    if not remote:
        FH.remove_quotes_from_file(path)


def main(args, path, remote_path, project):
    values = path.split("\\")
    zip_name = values[-1]
    save_path = path.replace(zip_name, "")
    name = zip_name.split(".zip")[0]
    zip_folder = f"{save_path}\\{name}"
    zip = f"{path}"
    copy_to = remote_path.replace(zip_name, "")
    create_folder(zip_folder)
    print("start unzip")
    FH.unzip(zip_file=zip, extract_folder=zip_folder)
    print(f"done unziping {zip}")
    run_auto_fa(path=zip_folder, project=project)
    FH.copy_res(main_folder=copy_to, path=zip_folder, name=name)
    print("Done Auto FA.")
    print("delete zip")
    try:
        FH.remove_file(file_path=zip)
    except Exception as e:
        print(e)
    return zip_folder


if __name__ == "__main__":
    parser = ArgumentParser(description='Automation FA.', epilog='REL Team FA Automation')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--path', type=str, help='path to result folder.')
    group.add_argument('--zip_path', type=str, help='path to zips folder.')
    parser.add_argument('--full_ctf', action='store_true')
    parser.add_argument('--full_vtf', action='store_true')
    parser.add_argument('--zip_file', type=str, help="is the folder zipped")
    parser.add_argument('--project', type=str, choices=['SPA', 'OBERON', 'OPHELIA'], required=True)
    args = parser.parse_args()
    if args.zip_file:
        tmp = str(args.zip_file).split("\\")[-1]
        zip_folder = f"{args.zip_file.split('.zip')[0]}"
        create_folder(zip_folder)
        FH.unzip(args.zip_file, zip_folder)
        print(f"done unziping {args.zip_file}")
        run_auto_fa(args, zip_folder, project=args.project)
    elif args.zip_path:
        zip_list = get_zip_file_list(args.zip_path)
        for zip in zip_list:
            name = f"{zip.split('.zip')[0]}"
            zip_folder = f"{args.zip_path}\\{zip.split('.zip')[0]}"
            zip = f"{args.zip_path}\\{zip}"
            create_folder(zip_folder)
            FH.unzip(zip, zip_folder)
            print(f"done unziping {zip}")
            run_auto_fa(args, zip_folder, project=args.project)
            FH.copy_res(main_folder=args.zip_path, path=zip_folder, name=name)
    else:
        run_auto_fa(path=args.path, project=args.project)
    print("Done Auto FA.")
