from argparse import ArgumentParser
import csv

import project as PRJ
import FileHandler as FH
import vtf_handler as VTF
import emonitor as EMonitor
import ProtocolLog as PL

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


def smartReport(main_folder, smart_report):
    FH.print_head_line("Smart Report")
    file_path = FH.getFilePath(main_folder, file_name="ROTWSmartReport.csv")
    if not file_path:
        return
    with open(f'{file_path}', encoding='utf-8', newline='') as csvf:
        reader = csv.reader(csvf)
        for row in reader:
            if row[0] in smart_report.keys():
                smart_report[f"{row[0]}"] = row[1]
    FH.write_file(folder_path=main_folder, section_name="SmartReport:", report=smart_report)


def emonitor_actions(path):
    FH.print_head_line("RWR Fast Scan")
    result = EMonitor.run_emonitor(args.path)
    emonitor_to_file = EMonitor.check_known_errors(result)
    FH.write_file(folder_path=path, section_name="RWR:", report=emonitor_to_file)


if __name__ == "__main__":
    parser = ArgumentParser(description='Automation FA.', epilog='REL Team FA Automation')
    parser.add_argument('--path', type=str, help='path to result folder.')
    parser.add_argument('--full_ctf', action='store_true')
    parser.add_argument('--project', type=str, choices=['SPA', 'OBERON'], required=True)
    # parser.add_argument('--full_vtf', action='store_true') \\ will be added with VTF Log error function
    args = parser.parse_args()
    current_project = PRJ.choose(args.project)
    vtf_data = vtf_info(args.path)
    ctf_log_error(args.path, args.full_ctf)
    smartReport(args.path, current_project.smartReport)
    emonitor_actions(args.path)
    protoco_log_info(args.path, vtf_data)
    print("Done Auto FA.")
