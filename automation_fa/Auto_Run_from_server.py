from argparse import ArgumentParser
from time import sleep

import auto_fa
import FileHandler as FH
import project as PRJ


if __name__ == "__main__":
    parser = ArgumentParser(description='Auto Run.', epilog='REL Team FA Automation')
    parser.add_argument('--path', type=str, help='path to result folder.')
    parser.add_argument('--full_ctf', action='store_true')
    parser.add_argument('--full_vtf', action='store_true')
    parser.add_argument('--project', type=str, choices=['SPA', 'OBERON'], default='OBERON')
    args = parser.parse_args()
    current_project = PRJ.choose(args.project)
    FH.create_folder(folder_path=args.path)
    #Please change the path to form \\*\*  to //*/* due to SMB access
    zips = FH.get_all_zips_in_path(remote_host="//10.24.8.10/tfnrel/Logs/oberon/10a.1124.282366")
    FH.write_file(folder_path="F:\\AutoFA", section_name="zips", report=zips)
    for zip in zips:
        try:
            did_fail = FH.check_if_fail(zip, "VTFLog.log")
            if did_fail:
                test = zip.split("\\")[-2]
                print(f"Issue on {test}")
                path = FH.copy_from_remote_path(remote_path=zip, folder_path=args.path)
                res_path = auto_fa.main(args, path=path, remote_path=zip, project=args.project)
                print("delete folder")
                FH.delete_folder(res_path)
                print("Done Auto FA.")
                sleep(1)
            else:
                test = zip.split("\\")[-2]
                print(f"{test} did Not failed, continue to the next one")
                sleep(1)
        except Exception as e:
            print(e)
            continue

