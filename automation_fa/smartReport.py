import FileHandler as FH
import logHandler as LOG


def get_smart_report(path, project_json):
    file_path = FH.getFilePath(original_file_path=path, file_name="SmartReport_Test*.json")
    if not file_path:
        return
    Smart_report = project_json
    data = LOG.get_json_data(file=file_path)
    data = data['ROTW_final']
    for key in project_json.keys():
        if key in data:
            Smart_report[f'{key}'] = data[f'{key}']
    FH.write_file(folder_path=path, section_name="SmartReport:", report=Smart_report)