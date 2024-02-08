import info_dictionary


class SFP:
    def __init__(self):
        self.smartReport = info_dictionary.SmartReportSPA
        self.protocol_log = "PROTOCOL*.csv"


class Oberon:
    def __init__(self):
        self.smartReport = info_dictionary.SmartReportOberon
        self.protocol_log = "protocol*.csv"

def choose(project):
    if project == "SPA":
        return SFP()
    if project == "OBERON":
        return Oberon()
