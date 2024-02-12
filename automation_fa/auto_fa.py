from argparse import ArgumentParser

import project as PRJ
import FileHandler as FH
import vtf_handler as VTF
import emonitor as EMonitor
import ProtocolLog as PL
import smartReport as SR


def vtf_info(path):
    FH.print_head_line("VTF Log")
    vtf_log = VTF.vtf_event2_info(path)
    FH.write_file(folder_path=path, section_name="VTF Log:", report=vtf_log)
    return vtf_log


def protoco_log_info(path, vtf):
    FH.print_head_line("protocol Log")
    res = PL.get_timestamp_event(path, vtf)
    FH.write_file(folder_path=path, section_name="Protocol log:", report=res)


def ctf_log_error(path, full_ctf_cmd):
    FH.print_head_line("CTF Log")
    file_path = FH.getFilePath(original_file_path=path, file_name="CTFLog.txt")
    if not file_path:
        return
    ctf_log = []
    with open(f'{file_path}', encoding='utf-8', newline='') as csvf:
        for line in csvf:
            if full_ctf_cmd:
                if "raising" and "exception" in line or "software" and "watchdog" in line or not line[0][0].isdigit():
                    if not len(line.strip()) == 0:
                        line = line.translate({ord(i): None for i in '\n\r\t'})
                        ctf_log.append(line)
            else:
                if "raising" and "exception" in line.lower() or "software" and "watchdog" in line.lower() \
                        and line[0][0].isdigit():
                    if not len(line.strip()) == 0:
                        line = line.translate({ord(i): None for i in '\n\r\t'})
                        ctf_log.append(line)
        FH.write_file(folder_path=args.path, section_name="CTFLog:", report=ctf_log)


def smartReport(main_folder, project_json):
    FH.print_head_line("Smart Report")
    SR.get_smart_report(main_folder, project_json=project_json)


def emonitor_actions(path):
    FH.print_head_line("RWR Fast Scan")
    rwr_files, rwr_issues = EMonitor.run_emonitor(args.path)
    FH.write_file(folder_path=path, section_name="RWR_Files:", report=rwr_files)
    FH.write_file(folder_path=path, section_name="RWR_issue:", report=rwr_issues)


if __name__ == "__main__":
    parser = ArgumentParser(description='Automation FA.', epilog='REL Team FA Automation')
    parser.add_argument('--path', type=str, help='path to result folder.')
    parser.add_argument('--full_ctf', action='store_true')
    parser.add_argument('--zip_file', action='store_true', help="is the folder zipped")
    parser.add_argument('--project', type=str, choices=['SPA', 'OBERON'], required=True)
    # parser.add_argument('--full_vtf', action='store_true') \\ will be added with VTF Log error function
    args = parser.parse_args()
    current_project = PRJ.choose(args.project)
    num = 0
    '''
        files_list = FH.getFilesPath(args.path, "zip", )
    for file in files_list:
    FH.unzip(args.path, zip_name=file,  folder_name="tmp")
    path = args.path
    path = args.path + "tmp"
    '''
    vtf_data = vtf_info(args.path)
    ctf_log_error(args.path, args.full_ctf)
    smartReport(args.path, project_json=current_project.smartReport)
    emonitor_actions(args.path)
    protoco_log_info(args.path, vtf_data)
    # shutil.copyfile(path + "\\REL_results.txt", args.path + f"\\REL_results{num}.txt")
    num = num + 1
    print("Done Auto FA.")
