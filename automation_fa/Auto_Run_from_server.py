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
    parser.add_argument('--amount_of_rwr', default=3, help="amount of RWR file from the last")
    parser.add_argument('--copy_single', type=str, default='')
    parser.add_argument('--path_copy', type=str, default='F:\\AutoFA')
    parser.add_argument('--file_path', type=str, default='')
    parser.add_argument('--project', type=str, choices=['SPA', 'OBERON'], default='OBERON')
    args = parser.parse_args()
    current_project = PRJ.choose(args.project)
    FH.create_folder(folder_path=args.path_copy)
    #Please change the path to form \\*\*  to //*/* due to SMB access
    if args.copy_single:
        zips_tmp = FH.copy_from_remote_path(remote_path=args.copy_single, folder_path=args.path)
        zips = [zips_tmp]
    elif args.file_path:
        zips = []
        with open(f'{args.file_path}', 'r') as file:
            data = file.readlines()
            for line in data:
                line = line.strip()
                zip = FH.get_zip_in_path(line)
                zips = zips + zip
    else:
        print("Getting all zip locations")
        zips = FH.get_all_zips_in_path(remote_host=args.path)
    FH.write_file(folder_path=args.path_copy, section_name="zips", report=zips)
    for zip in zips:
        try:
            print("check if faild")
            did_fail = FH.check_if_fail(zip, "VTFLog.log")
            if did_fail:
                test = zip.split("\\")[-2]
                print(f"Issue on {test}")
                if args.copy_single:
                    path = zip
                else:
                    path = FH.copy_from_remote_path(remote_path=zip, folder_path=args.path_copy)
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

