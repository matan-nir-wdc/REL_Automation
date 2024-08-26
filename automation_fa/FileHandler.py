import glob
import json
import os
import time
import pathlib
import shutil
import zipfile
from tqdm import tqdm
from typing import List, Dict, Union


def create_folder(folder_path="F:\\AutoFA\\tmp"):
    permissions = 0o777  # This sets read, write, execute permissions for owner and read, execute permissions for group and others
    try:
        os.mkdir(folder_path)
        os.chmod(folder_path, permissions)
        print(f"Folder '{folder_path}' created with permissions {oct(permissions)} successfully.")
    except Exception as e:
        print("An error occurred:", str(e))


def get_all_folders_in_path(path: str) -> List[str]:
    return [entry.path for entry in os.scandir(path) if entry.is_dir()]


def get_zip_in_path(remote_host):
    zips = []
    remote_host = remote_host.rstrip('\n')
    os.chdir(f"{remote_host}")
    current_sub_path = os.getcwd()
    zip_file = [f for f in os.listdir(current_sub_path) if
                os.path.isfile(os.path.join(current_sub_path, f)) and f.endswith('.zip')]
    if len(zip_file) > 0:
        zip_file = f"{current_sub_path}\\{zip_file[0]}"
        print(zip_file)
        zips.append(zip_file)
    return zips


def get_all_zips_in_path(remote_host):
    zips = []
    os.chdir(f"{remote_host}")
    folders = os.listdir()
    for folder in folders:
        current_path = os.getcwd() + "\\" + str(folder)
        print(f"Getting folders from {current_path}")
        sub_folders = [f for f in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, f))]
        for sub_folder in sub_folders:
            current_sub_path = current_path + "\\" + str(sub_folder)
            zip_file = []
            do_fa =True
            print(f"checking {current_sub_path}")
            for file in os.listdir(current_sub_path):
                # Check if any file ends with .txt
                if file.endswith('.txt'):
                    do_fa = False
            if do_fa:
                zip_file = [f for f in os.listdir(current_sub_path) if
                            os.path.isfile(os.path.join(current_sub_path, f)) and f.endswith('.zip')]
            if len(zip_file) > 0:
                zip_file = f"{current_sub_path}\\{zip_file[0]}"
                print(f"adding {zip_file} to FA testing list")
                zips.append(zip_file)
    return zips


def copy_from_remote_path(remote_path, folder_path=""):
    total_size = os.path.getsize(remote_path)
    copied_size = 0
    chunk_size = 1024 * 1024
    file_name = remote_path.split("\\")[-1]
    new_file_path = f"{folder_path}\\{file_name}"
    start_time = time.time()
    with open(remote_path, 'rb') as source_file, open(new_file_path, 'wb') as dest_file:
        while True:
            chunk = source_file.read(chunk_size)
            if not chunk:
                break
            dest_file.write(chunk)
            copied_size += len(chunk)

            # Calculate and display progress
            progress = copied_size / total_size * 100
            print(f"\rProgress: {progress:.2f}%", end='')

    end_time = time.time()
    print(f"\nCopy complete. Time taken: {end_time - start_time:.2f} seconds")
    return new_file_path


def write_file(folder_path, section_name, report, file_name="REL_results.txt"):
    with open(f'{folder_path}\\{file_name}', 'a+', encoding='utf-8') as f:
        f.write(section_name + "\n")
        if all(isinstance(item, tuple) for item in report):
            for item in report:
                f.write(str(item))
                f.write("\n")
        elif isinstance(report, list):
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


def getFilesPath(path: str, exception: str) -> List[str]:
    return [str(file) for file in pathlib.Path(path).glob(f'*.{exception}')]


def extract_event_from_file(file_path: str, target_phrase: str) -> List[str]:
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        found = [i for i, line in enumerate(lines) if target_phrase.lower() in line.lower()]
        if len(found) >= 2:
            return lines[found[0]:found[1]]
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def remove_file(file_path: str):
    try:
        os.chmod(file_path, 0o777)
        pathlib.Path(file_path).unlink()
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")


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
        shutil.rmtree(path)
        print(f"Folder '{path}' and its contents have been successfully deleted.")
    except Exception as e:
        print(f"An error occurred while deleting the folder: {e}")


def unzip(zip_file, extract_folder):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        for file in tqdm(file_list, desc="Extracting"):
            zip_ref.extract(file, extract_folder)
    print("deleting zip file")
    os.remove(path=f"{zip_file}")


def remove_quotes_from_file(path):
    with open(f'{path}\\REL_results.txt', 'r') as f, open(f'{path}\\REL_result.txt', 'w') as fo:
        for line in f:
            fo.write(line.replace('"', '').replace("'", ""))
    remove_file(file_path=f'{path}\\REL_results.txt')


def copy_res(main_folder, path, name):
    with open(f'{path}\\REL_result.txt', 'r') as file:
        data = file.readlines()
        if "Only PMI found, FA logs clean" in data[1]:
                name = "PMI ISSUE"
        elif "lane0_falling over 1K, FA logs clean" in data[1]:
            name = "NAC ISSUE"
    shutil.copy(f'{path}\\REL_result.txt', main_folder)
    shutil.copy(f'{path}\\FAST_SCAN.txt', main_folder)
    try:
        os.rename(f"{main_folder}\\REL_result.txt", f"{main_folder}\\{name}.txt")
    except Exception as e:
        print(e)
        pass


def combine_files(first_file_path, sec_file_path):
    # Open the first file in append mode and the second file in read mode
    with open(first_file_path, 'a') as write_obj, open(sec_file_path, 'r') as read_obj:
        for line in read_obj:
            write_obj.write(line)

    # Remove the second file
    os.remove(sec_file_path)


def get_all_keys(nested_dict, parent_key=''):
    res = {}
    for k, v in nested_dict.items():
        full_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            res.update(get_all_keys(v, full_key))
        else:
            res[k] = v
    return res
