import glob
import json
import os
import pathlib
import shutil
import zipfile


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
    file_to_rem = pathlib.Path(f"{path}\\{file}")
    file_to_rem.unlink()


def unzip(path, zip_name, folder_name):
    with zipfile.ZipFile(f"{path}\\{zip_name}", 'r') as zip_ref:
        zip_ref.extractall(folder_name)


def remove_quotes_from_file(path):
    with open(f'{path}\\REL_results.txt', 'r') as f, open(f'{path}\\REL_result.txt', 'w') as fo:
        for line in f:
            fo.write(line.replace('"', '').replace("'", ""))
    remove_file(path=f'{path}', file='REL_results.txt')


def copy_res(main_folder, path, name):
    shutil.copy(f'{path}\\REL_result.txt', main_folder)
    os.rename(f"{main_folder}\\REL_result.txt", f"{main_folder}\\{name}.txt")