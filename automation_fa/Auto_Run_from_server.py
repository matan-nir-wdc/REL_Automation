import os
import time
from datetime import datetime, timedelta
from argparse import ArgumentParser
import auto_fa
import FileHandler as FH
import po_report as PO_REP
import project as PRJ
import gc


def running_zip_list(zips_list, project, fw):
    for zip_file in zips_list:
        try:
            # Split to get the second last directory as the test identifier
            test = zip_file.split("\\")[-2]
            print(f"Issue on {test}")

            # Copy the file from the remote path
            path = FH.copy_from_remote_path(remote_path=zip_file, folder_path=args.path_copy)
            values = path.split("\\")
            zip_name = values[-1]  # Get the zip file name
            save_path = path.replace(zip_name, "")  # Directory without the zip name

            # Extract folder name from zip file name
            name = zip_name.split(".zip")[0]
            zip_folder = f"{save_path}\\{name}"
            new_path = "\\".join(zip_file.split("\\")[:-1])  # Remote folder path

            # Create folder for extraction
            auto_fa.create_folder(zip_folder)

            print("Start unzipping")
            # Unzip the file into the created folder
            FH.unzip(zip_file=path, extract_folder=zip_folder, main_folder=save_path, zip_failed=zip_file)
            print(f"Done unzipping {path}")

            # Run the Auto FA process
            auto_fa.run_auto_fa(path=zip_folder, project=args.project, remote=True)
            file_name = PO_REP.create_file(path=save_path, project=project, fw=fw)
            PO_REP.add_data(data=zip_folder, file_path=file_name, zip_path=zip_file)
            # Copy results to the remote directory
            FH.remove_quotes_from_file(path=f"{zip_folder}")
            FH.copy_res(main_folder=new_path, path=zip_folder, name=name)
            gc.collect()
            print("Done Auto FA.")

            # Delete the extracted folder after processing
            print("Deleting extracted folder")
            FH.delete_folder(zip_folder)
            print("Completed cleanup.")

        except Exception as e:
            print(f"An error occurred with {zip_file}: {e}")


if __name__ == "__main__":
    parser = ArgumentParser(description='Auto Run.', epilog='REL Team FA Automation')
    parser.add_argument('--path', type=str, help='path to result folder.')
    parser.add_argument('--full_vtf', action='store_true')
    parser.add_argument('--copy_single', type=str, default='')
    parser.add_argument('--path_copy', type=str, default='C:\\AutoFA')
    parser.add_argument('--main_fa_folder', type=str, default='')
    parser.add_argument('--file_path', type=str, default='')
    parser.add_argument('--project', type=str, choices=['SPA', 'OBERON', 'OPHELIA'], default='OPHELIA')
    args = parser.parse_args()
    current_project = PRJ.choose(args.project)
    FH.create_folder(folder_path=args.path_copy)

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
                last_24_hours = now - timedelta(hours=168)
                # Iterate through all folders in the root folder
                for fw_folder in os.listdir(args.main_fa_folder):
                    fw_folder_path = os.path.join(args.main_fa_folder, fw_folder)
                    zips_list = []
                    for folder_name in os.listdir(fw_folder_path):
                        folder_path = os.path.join(fw_folder_path, folder_name)
                        for folder_name_2 in os.listdir(folder_path):
                            folder_path_2 = os.path.join(folder_path, folder_name_2)
                            # Check if it's a directory
                            print(f"Checking {folder_name_2} now")
                            if os.path.isdir(folder_path_2):
                                # Get the folder's creation time
                                folder_creation_time = datetime.fromtimestamp(os.path.getctime(folder_path_2))
                                #   Check if the folder was created within the last 24 hours
                                if folder_creation_time > last_24_hours or True:
                                    # Check for ZIP files in the folder
                                    zip = ""
                                    has_fast_scan = False
                                    for file in os.listdir(folder_path_2):
                                        if file.endswith('.zip'):
                                            zip = file
                                        if file == "FAST_SCAN.csv":
                                            has_fast_scan = True
                                    if (not has_fast_scan) and zip:
                                        zip_full_path = os.path.join(folder_path_2, zip)
                                        print(f"Found issue in {zip_full_path}")
                                        zips_list.append(zip_full_path)
                    if zips_list:
                        print(f"Found ZIP files: {zips_list}")
                        print("Amount of zips found: " + str(len(zips_list)))
                        running_zip_list(zips_list, project=args.project, fw=fw_folder)
                        print("Removing remain folders")
                        FH.remove_folders(path=args.path_copy)
                        print("sleep for 10 minutes")
                        time.sleep(600)  # Sleep for 60 seconds before checking again
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                print(error_message)
                break

