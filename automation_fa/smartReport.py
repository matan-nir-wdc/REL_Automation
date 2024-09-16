import FileHandler as FH
import logHandler as LOG


def get_smart_report(path, project_json):
    Smart_report = project_json
    SRF = FH.get_all_folders_in_path(path=path)
    data = ""
    for new_path in SRF:
        file_path = FH.getFilePath(original_file_path=new_path, file_name="SmartReport.json")
        if file_path:
            data = LOG.get_json_data(file=file_path)
            data = data["ROTW_final"]
            break
    if not data:
        return False

    for key in project_json.keys():
        if key in data:
            Smart_report[f'{key}'] = data[f'{key}']
    keys = ["bitflipCorrectionCounter", "badBlockRuntimeIs", "badBlockRuntimeMlc", "eraseFailCount", "progFailCount",
            "ueccInMarkedBlockCount", "uncorrectableErrorCorrectionCode"]
    write_values = []
    for key in keys:
        if Smart_report[f'{key}'] != 0:
            write_values.append(key)
    write_values = ' '.join(write_values)
    if write_values:
        FH.write_file(folder_path=path, section_name="", report=write_values + " Are high, please check!!!")
        FH.write_file(folder_path=path, section_name="SmartReport:", report=Smart_report)
        return True
    FH.write_file(folder_path=path, section_name="SmartReport:", report=Smart_report)
    return False
