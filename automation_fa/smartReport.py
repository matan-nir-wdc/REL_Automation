import FileHandler as FH
import csv_handler as CSV


def get_smart_report(path, project_json):
    file_path = FH.getFilePath(original_file_path=path, file_name="ROTWSmartReport.csv")
    report = []
    if not file_path:
        return
    data = CSV.get_data(file=file_path, names=["key", "val1", "val2", "val3"])
    data = data.iloc[:, 0:2]
    for key in project_json.keys():
        res = CSV.return_signle_event(data=data, header="key", value=key)
        res = res.to_string(justify='left', index=False)
        res = res.split('\n')[1]
        report.append(res)
    FH.write_file(folder_path=path, section_name="SmartReport:", report=report)
