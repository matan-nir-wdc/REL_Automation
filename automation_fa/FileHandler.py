import glob
import json
import os
import pathlib
import shutil
import zipfile
from tqdm import tqdm

def create_folder(folder_path="F:\\AutoFA\\tmp"):
    permissions = 0o777  # This sets read, write, execute permissions for owner and read, execute permissions for group and others
    try:
        os.mkdir(folder_path)
        os.chmod(folder_path, permissions)
        print(f"Folder '{folder_path}' created with permissions {oct(permissions)} successfully.")
    except Exception as e:
        print("An error occurred:", str(e))



def get_all_folders_in_path(path):
    folders = [entry.path for entry in os.scandir(path) if entry.is_dir()]
    return folders
def get_all_zips_in_path(remote_host):
    zips = []
    os.chdir(f"{remote_host}")
    folders = os.listdir()
    for folder in folders:
        current_path = os.getcwd() + "\\" + str(folder)
        sub_folders = [f for f in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, f))]
        for sub_folder in sub_folders:
            current_sub_path = current_path + "\\" + str(sub_folder)
            zip_file = [f for f in os.listdir(current_sub_path) if
                        os.path.isfile(os.path.join(current_sub_path, f)) and f.endswith('.zip')]
            if len(zip_file) > 0:
                zip_file = f"{current_sub_path}\\{zip_file[0]}"
                zips.append(zip_file)
    return zips


def copy_from_remote_path(remote_path, folder_path=""):
    chunk_size = 1024
    file_name = remote_path.split("\\")[-1]
    new_file_path = f"{folder_path}\\{file_name}"
    try:
        # Get the size of the source file
        total_size = os.path.getsize(remote_path)
        bytes_copied = 0

        # Open source file for reading in binary mode
        with open(remote_path, 'rb') as source_file:
            # Open destination file for writing in binary mode
            with open(new_file_path, 'wb') as destination_file:
                while True:
                    # Read a chunk of data from the source file
                    chunk = source_file.read(chunk_size)
                    if not chunk:
                        # End of file reached
                        break
                    # Write the chunk to the destination file
                    destination_file.write(chunk)
                    # Update bytes_copied
                    bytes_copied += len(chunk)
                    # Calculate and print the percentage
                    percentage = (bytes_copied / total_size) * 100
                    print(f"Copying... {percentage:.2f}% done", end='\r')

        print("File copied successfully.")
        return new_file_path
    except Exception as e:
        print("An error occurred:", str(e))


def write_file(folder_path, section_name, report):
    with open(f'{folder_path}\\REL_results.txt', 'a', encoding='utf-8') as f:
        f.write(section_name + "\n")
        if isinstance(report, list):
            json_report = '\n'.join(report)
            f.write(str(json_report))
        elif isinstance(report, dict):
            json.dump(report, f, ensure_ascii=True, indent=4)
        elif isinstance(report, str):
            f.write(report)
        f.write("\n\n")


def print_head_line(file_name):
    print(f"\n========================= Analysing {file_name} =========================\n")


def getFilePath(original_file_path, file_name):
    try:
        res = glob.glob(f'{original_file_path}\\**\\{file_name}', recursive=True)[0]
    except IndexError as e:
        print(f"No {file_name} found")
        return ""
    return res


def getFilesPath(path, exception):
    files = []
    for file in os.listdir(f"{path}"):
        if file.endswith(f".{exception}"):
            files.append(os.path.join(f"{path}", file))
    return files


def extract_event_from_file(file_path, target_phrase):
    try:
        found = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line_num, line in enumerate(lines):
                if target_phrase in line.lower():
                    found.append(line_num)
                    if len(found) == 2:
                        return lines[found[0]:found[1]]
    except Exception as e:
        print(f"An error occurred: {e}")


def remove_file(path, file):
    permissions = 0o777  # This sets read, write, execute permissions for owner and read, execute permissions for group and others
    os.chmod(f"{path}\\{file}", permissions)
    file_to_rem = pathlib.Path(f"{path}\\{file}")
    file_to_rem.unlink()


def check_if_fail(zip_file, file_name):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        with zip_ref.open(file_name) as file:
            content = file.read().decode('utf-8')
            if "signature: TestStatus.PASS" in content:
                return False
    return True


def delete_folder(path):
    try:
        permissions = 0o777  # This sets read, write, execute permissions for owner and read, execute permissions for group and others
        os.chmod(f"{path}", permissions)
        os.remove(path=path)
        print(f"Folder '{path}' and its contents have been successfully deleted.")
    except Exception as e:
        print(f"An error occurred while deleting the folder: {e}")


def unzip(zip_file, extract_folder):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        for file in tqdm(file_list, desc="Extracting"):
            zip_ref.extract(file, extract_folder)
    print("deleting zip file")
    #permissions = 0o777  # This sets read, write, execute permissions for owner and read, execute permissions for group and others
    #os.chmod(f"{zip_file}", permissions)
    os.remove(path=f"{zip_file}")



def remove_quotes_from_file(path):
    with open(f'{path}\\REL_results.txt', 'r') as f, open(f'{path}\\REL_result.txt', 'w') as fo:
        for line in f:
            fo.write(line.replace('"', '').replace("'", ""))
    remove_file(path=f'{path}', file='REL_results.txt')


def copy_res(main_folder, path, name):
    shutil.copy(f'{path}\\REL_result.txt', main_folder)
    os.rename(f"{main_folder}\\REL_result.txt", f"{main_folder}\\{name}.txt")
