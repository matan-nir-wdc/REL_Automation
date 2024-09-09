import os
import time
from datetime import datetime, timedelta
from argparse import ArgumentParser
import auto_fa
import FileHandler as FH
import project as PRJ


def running_zip_list(zips_list):
    for zip in zips_list:
        try:
            test = zip.split("\\")[-2]
            print(f"Issue on {test}")
            path = FH.copy_from_remote_path(remote_path=zip, folder_path=args.path_copy)
            values = path.split("\\")
            zip_name = values[-1]
            save_path = path.replace(zip_name, "")
            name = zip_name.split(".zip")[0]
            zip_folder = f"{save_path}\\{name}"
            new_path = "\\".join(zip.split("\\")[:-1])
            zip = f"{path}"
            auto_fa.create_folder(zip_folder)
            print("start unzip")
            FH.unzip(zip_file=zip, extract_folder=zip_folder)
            print(f"done unziping {path}")
            auto_fa.run_auto_fa(path=zip_folder, project=args.project)
            FH.copy_res(main_folder=new_path, path=zip_folder, name=name)
            print("Done Auto FA.")
            print("delete zip")
            FH.delete_folder(zip_folder)
            print("Done Auto FA.")

        except Exception as e:
            print(e)

if __name__ == "__main__":
    parser = ArgumentParser(description='Auto Run.', epilog='REL Team FA Automation')
    parser.add_argument('--path', type=str, help='path to result folder.')
    parser.add_argument('--full_vtf', action='store_true')
    parser.add_argument('--copy_single', type=str, default='')
    parser.add_argument('--path_copy', type=str, default='C:\\AutoFA')
    parser.add_argument('--main_fa_folder', type=str, default='')
    parser.add_argument('--file_path', type=str, default='')
    parser.add_argument('--project', type=str, choices=['SPA', 'OBERON', 'OPHILIA'], default='OPHILIA')
    args = parser.parse_args()
    current_project = PRJ.choose(args.project)
    FH.create_folder(folder_path=args.path_copy)
    zips_list = []
    # Please change the path to form \\*\*  to //*/* due to SMB access
    if args.copy_single:
        zips_tmp = FH.copy_from_remote_path(remote_path=args.copy_single, folder_path=args.path)
        zips = [zips_tmp]
    elif args.file_path:
        with open(f'{args.file_path}', 'r') as file:
            data = file.readlines()
            for line in data:
                line = line.strip()
                zip = FH.get_zip_in_path(line)
                zips_list = zips_list + zip
    else:
        print("Getting all zip locations")
        while True:
            try:
                now = datetime.now()
                # Calculate 24 hours ago
                last_24_hours = now - timedelta(hours=250)
                # Iterate through all folders in the root folder
                for folder_name in os.listdir(args.main_fa_folder):
                    folder_path = os.path.join(args.main_fa_folder, folder_name)
                    for folder_name_2 in os.listdir(folder_path):
                        folder_path_2 = os.path.join(folder_path, folder_name_2)
                    # Check if it's a directory
                        print(f"Checking {folder_name_2} now")
                        if os.path.isdir(folder_path_2):
                            # Get the folder's creation time
                            folder_creation_time = datetime.fromtimestamp(os.path.getctime(folder_path_2))
                            #   Check if the folder was created within the last 24 hours
                            if folder_creation_time > last_24_hours:
                                # Check for ZIP files in the folder
                                zip = ""
                                has_fast_scan = False
                                for file in os.listdir(folder_path_2):
                                    if file.endswith('.zip'):
                                        zip = file
                                    if file == "FAST_SCAN.csv":
                                        has_fast_scan = True
                                if not has_fast_scan and zip:
                                    zip_full_path = os.path.join(folder_path_2, file)
                                    print("check if faild")
                                    #did_fail = FH.check_if_fail(zip_full_path, "VTFLog.log")
                                    did_fail = True
                                    if did_fail:
                                        print(f"Found issue in {file}")
                                        zips_list.append(zip_full_path)
                        # If there are any ZIP files, run run_fa()
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                print(error_message)
                break
    if zips_list:
        print(f"Found ZIP files: {zips_list}")
        running_zip_list(zips_list)
        time.sleep(60)  # Sleep for 60 seconds before checking again

