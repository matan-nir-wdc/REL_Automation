import os
import shutil
import time
import gc
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from argparse import ArgumentParser
import auto_fa
import FileHandler as FH
import po_report as PO_REP
import project as PRJ


def check_file(file_path, zip_path):
    """Check if the zip path is referenced in the file."""
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if zip_path in line:
                    return True
        return False
    except FileNotFoundError:
        print(f"The file '{file_path}' does not exist.")
        return None


def process_zip_file(zip_file, project, fw, main_fa_folder, path_copy):
    """Process each zip file: unzip, run FA, and post-process results."""
    try:
        print(f"Running {zip_file}")
        save_path = main_fa_folder
        file_name = PO_REP.create_file(path=save_path, project=project, fw=fw)
        failed_zip = check_file(file_path=file_name, zip_path=zip_file)

        if failed_zip is None or not failed_zip:
            test = zip_file.split("\\")[-2]
            print(f"Issue on {test}")

            # Copy the file from the remote path
            path = FH.copy_from_remote_path(remote_path=zip_file, folder_path=path_copy)
            zip_name = os.path.basename(zip_file).split(".zip")[0]
            zip_folder = os.path.join(save_path, zip_name)
            new_path = os.path.dirname(zip_file)

            # Create folder for extraction and unzip
            auto_fa.create_folder(zip_folder)
            print(f"{zip_file} failed - Start unzipping")
            FH.unzip(zip_file=path, extract_folder=zip_folder, main_folder=save_path, zip_failed=zip_file)
            print(f"Done unzipping {path}")

            # Run the Auto FA process
            auto_fa.run_auto_fa(path=zip_folder, project=project, remote=True)
            PO_REP.add_data(data=zip_folder, file_path=file_name, zip_path=zip_file)

            # Post-processing
            FH.remove_quotes_from_file(path=zip_folder)
            FH.copy_res(main_folder=new_path, path=zip_folder, name=zip_name)
            gc.collect()

            # Cleanup
            print(f"Deleting extracted folder {zip_folder}")
            FH.delete_folder(zip_folder)
            print("Completed cleanup.")
        else:
            print("Zip file is a known issue, skipping.")
    except Exception as e:
        print(f"An error occurred with {zip_file}: {e}")


def running_zip_list(zips_list, project, fw, main_fa_folder, path_copy):
    """Run Auto FA on a list of ZIP files concurrently."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future_to_zip = {executor.submit(process_zip_file, zip_file, project, fw, main_fa_folder, path_copy): zip_file for zip_file in zips_list}

        for future in as_completed(future_to_zip):
            zip_file = future_to_zip[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing {zip_file}: {e}")


if __name__ == "__main__":
    parser = ArgumentParser(description='Auto Run.', epilog='REL Team FA Automation')
    parser.add_argument('--path', type=str, help='Path to result folder.')
    parser.add_argument('--full_vtf', action='store_true')
    parser.add_argument('--copy_single', type=str, default='')
    parser.add_argument('--path_copy', type=str, default='C:\\AutoFA')
    parser.add_argument('--main_fa_folder', type=str, default='')
    parser.add_argument('--file_path', type=str, default='')
    parser.add_argument('--project', type=str, choices=['SPA', 'OBERON', 'OPHELIA'], default='OPHELIA')
    args = parser.parse_args()

    current_project = PRJ.choose(args.project)
    FH.create_folder(folder_path=args.path_copy)

    zips_list = []

    if args.copy_single:
        zips_tmp = FH.copy_from_remote_path(remote_path=args.copy_single, folder_path=args.path)
        zips_list = [zips_tmp]
    elif args.file_path:
        with open(args.file_path, 'r') as file:
            zips_list = [FH.get_zip_in_path(line.strip()) for line in file.readlines()]
    else:
        print("Getting all zip locations")
        while True:
            try:
                now = datetime.now()
                last_24_hours = now - timedelta(hours=168)

                for fw_folder in os.listdir(args.main_fa_folder):
                    fw_folder_path = os.path.join(args.main_fa_folder, fw_folder)

                    for folder_name in os.listdir(fw_folder_path):
                        folder_path = os.path.join(fw_folder_path, folder_name)

                        for folder_name_2 in os.listdir(folder_path):
                            folder_path_2 = os.path.join(folder_path, folder_name_2)
                            print(f"Checking {folder_name_2} now")

                            if os.path.isdir(folder_path_2):
                                folder_creation_time = datetime.fromtimestamp(os.path.getctime(folder_path_2))

                                if folder_creation_time > last_24_hours:
                                    zip_file = ""
                                    has_fast_scan = False
                                    for file in os.listdir(folder_path_2):
                                        if file.endswith('.zip'):
                                            zip_file = file
                                        if file == "FAST_SCAN.csv":
                                            has_fast_scan = True

                                    if (not has_fast_scan) and zip_file:
                                        zip_full_path = os.path.join(folder_path_2, zip_file)
                                        print(f"Found issue in {zip_full_path}")
                                        zips_list.append(zip_full_path)

                if zips_list:
                    print(f"Found ZIP files: {zips_list}")
                    print(f"Amount of zips found: {len(zips_list)}")
                    running_zip_list(zips_list, project=args.project, fw=fw_folder, main_fa_folder=args.path_copy, path_copy=args.path_copy)
                    FH.remove_folders(path=args.path_copy)

                    # Copy PO reports to remote folder
                    po_report_folder = r"\\10.24.8.10\tfnrel\temp\PO_report"
                    for file in os.listdir(args.path_copy):
                        source_file_path = os.path.join(args.path_copy, file)
                        if os.path.isfile(source_file_path) and (file.endswith('.txt') or file.endswith('.csv')):
                            destination_file_path = os.path.join(po_report_folder, file)
                            shutil.copy2(source_file_path, destination_file_path)
                            print(f"Copied {source_file_path} to {destination_file_path}")

                    print("Going to sleep for 1 hour")
                    time.sleep(3600)
                else:
                    print("No zip files found, sleeping for 20 minutes.")
                    time.sleep(1200)
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                break
