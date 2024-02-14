import logHandler as LOG
import FileHandler as FH


def get_ctf_data(path, full_ctf_cmd, vtf_data):
    file = FH.getFilePath(original_file_path=path, file_name="CTFLog.txt")
    res = LOG.get_data(file)
    ctf_log = []
    uid = vtf_data['UID']
    for line in res:
        if full_ctf_cmd:
            if "raising" and "exception" in line or "software" and "watchdog" in line or not line[0][0].isdigit():
                if not len(line.strip()) == 0:
                    line = line.translate({ord(i): None for i in '\n\r\t'})
                    ctf_log.append(line)
        else:
            if "raising" and "exception" in line.lower() or "software" and "watchdog" in line.lower() \
                    and line[0][0].isdigit():
                if not len(line.strip()) == 0:
                    line = line.translate({ord(i): None for i in '\n\r\t'})
                    ctf_log.append(line)

    show_uid = ["\nUID show in CTF Log:"]
    for line in res:
        if str(uid) in line:
            show_uid.append(line)
    if len(show_uid) > 1:
        ctf_log = ctf_log + show_uid
    FH.write_file(folder_path=path, section_name="CTFLog:", report=ctf_log)
