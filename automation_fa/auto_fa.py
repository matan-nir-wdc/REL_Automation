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
    rwr_files, rwr_issues = EMonitor.run_emonitor(args.path)
    FH.write_file(folder_path=path, section_name="RWR_Files:", report=rwr_files)
    FH.write_file(folder_path=path, section_name="RWR_issue:", report=rwr_issues)


if __name__ == "__main__":
    parser = ArgumentParser(description='Automation FA.', epilog='REL Team FA Automation')
    parser.add_argument('--path', type=str, help='path to result folder.')
    parser.add_argument('--full_ctf', action='store_true')
    parser.add_argument('--full_vtf', action='store_true')
    parser.add_argument('--zip_file', action='store_true', help="is the folder zipped")
    parser.add_argument('--project', type=str, choices=['SPA', 'OBERON'], required=True)
    args = parser.parse_args()
    current_project = PRJ.choose(args.project)
    vtf_data = vtf_info(args.path)
    ctf_log_error(args.path, args.full_ctf, vtf_data)
    smartReport(args.path, project_json=current_project.smartReport)
    emonitor_actions(args.path)
    protoco_log_info(args.path, vtf_data)
    FH.remove_quotes_from_file(args.path)
    print("Done Auto FA.")
