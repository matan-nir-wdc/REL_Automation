import FileHandler as FH
import logHandler as LOG


def get_smart_report(path, project_json):
    data = ""
    Smart_report = project_json
    SRF = FH.get_all_folders_in_path(path=path)
    file_path = FH.getFilePath(original_file_path=SRF[0], file_name="SmartReport.json")
    if file_path:
        data = LOG.get_json_data(file=file_path)
        data = data["ROTW_final"]
    elif not file_path:
        file_path = FH.getFilePath(original_file_path=path, file_name="SmartReport_Test*.json")
        if not file_path:
            print("No smart report was found")
            return
        data = LOG.get_json_data(file=file_path)
        data = data["ROTW_final"]
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
        return True
    FH.write_file(folder_path=path, section_name="SmartReport:", report=Smart_report)
    return False
