import json
import FileHandler as FH


def get_pdl_file(path):
    folders = FH.get_all_folders_in_path(path)
    file_path = ""
    for folder in folders:
        file_path = FH.getFilePath(original_file_path=folder, file_name="PDL*.json")
        if file_path:
            return file_path
    if not file_path:
        print("Need to check manually")
        return None


def check_for_err_fail(pdl_file):
    with open(pdl_file, 'r') as file:
        data = json.load(file)
        pdl_print = {}
    for key in data.keys():
        tmp_data = data[key]
        for sec_key in tmp_data.keys():
            if "Error" in sec_key or "Failure" in sec_key:
                if tmp_data[sec_key] > 0:
                    pdl_print[sec_key] = tmp_data[sec_key]
    return pdl_print

