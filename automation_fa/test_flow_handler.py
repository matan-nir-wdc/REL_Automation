import json
from vtf_handler import get_test_name
from FileHandler import write_file

def load_test(project):
    with open("automation_fa/Jason_Value/test_flow.json", encoding="utf-8", mode="r") as js:
        data = js.read()
    data = json.loads(data)
    return data[f"{project}"]

def get_test_flow(path, project):
    test_flow = load_test(project=project)
    test_name = get_test_name(path=path)
    for key in test_flow:
        if key in test_name:
            write_file(folder_path=path, section_name="Test Flow in HT:", report='\n'.join(test_flow[f"{key}"]))
            return
    print("Could NOT find the test")

if __name__ == "__main__":
    get_test_flow(path="C:\issue\TestDLTHost__10Percent_Full_20240412_153544_16641", project="OBERON")
