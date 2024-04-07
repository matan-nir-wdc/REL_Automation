import FileHandler as FH
import logHandler as LOG


def get_smart_report(path, project_json):
    file_path = FH.getFilePath(original_file_path=path, file_name="SmartReport_Test*.json")
    main_key = "ROTW_final"
    data_check = False
    if not file_path:
        file_path = FH.getFilePath(original_file_path=path, file_name="SmartReportFull.json")
        data_check = True
        if not file_path:
            print("No smart report was found")
            return
    Smart_report = project_json
    data = LOG.get_json_data(file=file_path)
    if data_check:
        main_key = list(data.keys())[0]
    data = data[f'{main_key}']
    for key in project_json.keys():
        if key in data:
            Smart_report[f'{key}'] = data[f'{key}']
    FH.write_file(folder_path=path, section_name="SmartReport:", report=Smart_report)
