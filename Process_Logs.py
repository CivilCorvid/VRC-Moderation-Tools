def write_data_to_database(events_log, database_filename):
    import sqlite3
    db_connection = sqlite3.connect(database_filename)
    pointer = db_connection.cursor()
    pointer.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                userid TEXT NOT NULL,
                time INTEGER NOT NULL,
                event TEXT NOT NULL,
                subevent TEXT NOT NULL
            )
        ''')
    pointer.executemany("INSERT INTO events (username, userid, time, event, subevent) VALUES (?, ?, ?, ?, ?)", events_log)

    # Commit and close
    db_connection.commit()
    db_connection.close()
    return True

def process_logs(text_file_data, source_path, username, userid):
    import datetime
    # List of events to be tracked:
    track_events = [
        "[Behaviour] Joining wrld", #eg.  [Behaviour] Joining wrld_074e42c2-c117-415d-817a-452a67c95200:28421~group(grp_9a2be521-7faa-432b-9171-f15313e4daef)~groupAccessType(public)~region(us)
        "[Behaviour] Entering Room: ",
        "[Behaviour] OnPlayerLeft ",
        "[Behaviour] OnPlayerJoined ",
        " Error      -"
    ]
    events_log = []
    # Events format: time, event, sub-event
    time_info = get_log_time(text_file_data, source_path)
    time_created, time_modified, filename_timestamp, text_file_data_timestamp, utc_offset = time_info

    for line in text_file_data:
        for event in track_events:
            if event in line:

                # Do thing here
                split_line = line.split(" ")

                # Finding what time it is.
                line_date = split_line[0]
                line_hour = split_line[1]
                dt = datetime.datetime.strptime(f"{line_date} {line_hour}", "%Y.%m.%d %H:%M:%S")
                dt -= datetime.timedelta(hours=utc_offset)
                unix_time = int(dt.timestamp())

                # sub-event data
                sub_event = line.split(event)[-1]
                event_info = [unix_time, username, userid, event, sub_event]
                events_log.append(event_info)

    return events_log



def get_utc_offset(time_created, filename_timestamp):
    import datetime
    filename_dt = datetime.datetime.strptime(filename_timestamp, "%Y-%m-%d %H-%M-%S")
    time_created_dt = datetime.datetime.fromtimestamp(time_created)

    # Offset in seconds
    offset_seconds = (time_created_dt - filename_dt).total_seconds()
    offset_hours = offset_seconds / 3600
    return offset_hours

def get_log_time(text_file_data, filename):
    from os import path
    # Filename example: output_log_2025-01-27_20-18-20.txt
    # text_file_data example: 2025.01.28 20:14:53 Log
    time_created = path.getctime(filename)
    time_modified = path.getmtime(filename)
    filename_timestamp = filename.split("output_log_")[-1].split(".")[0].replace("_"," ")
    text_file_data_timestamp = text_file_data[0].split(" Log")[0]
    utc_offset = get_utc_offset(time_created, filename_timestamp)
    return time_created, time_modified, filename_timestamp, text_file_data_timestamp, utc_offset

def get_vrc_build_version(text_file_data):
    for line in text_file_data:
        if "VRChat Build:" in line:
            return line.replace("VRChat Build:","").replace(" ","").replace("\n","")

def get_author(text_file_data):
    for line in text_file_data:
        if "User Authenticated: " in line:
            user_string = line.split("User Authenticated: ")[-1].replace("\n","")
            username = user_string.split(" (usr")[0]
            userid = user_string.replace(username + " ", "").replace(")","").replace("(","")
            return username, userid

def package_text_data(filename):
    text_file_data = []

    # Load file data into array and then close the file.
    with open(filename, "r", encoding="utf-8") as logfile:
        for line in logfile:
            text_file_data.append(line)
    return text_file_data

    #
