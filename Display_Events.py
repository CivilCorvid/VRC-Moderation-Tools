def get_events(DATABASE_FILE):
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, userid, time, event, subevent 
        FROM events 
        ORDER BY userid, time
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def process_sessions(events):
    import datetime
    sessions_by_user = {}
    duplicate_threshold = 5  # seconds

    for event in events:
        print(event)
        timestamp, username, userid, event, subevent = event
        print(username, userid, timestamp, event)
        timestamp = int(timestamp)
        if event in ("[Behaviour] OnPlayerJoined ", "[Behaviour] OnPlayerLeft ", "[Behaviour] OnPlayerLeftRoom", "[Player] OnApplicationQuit"):
            if subevent not in sessions_by_user:
                sessions_by_user[subevent] = {"username": subevent, "sessions": []}

            user_sessions = sessions_by_user[subevent]["sessions"]
            #print(user_sessions)
            if event == "[Behaviour] OnPlayerJoined ":
                if user_sessions and user_sessions[-1]["end"] is None:
                    if timestamp - user_sessions[-1]["start"] < duplicate_threshold:
                        continue
                user_sessions.append({"start": timestamp, "end": None})

            # If player leaves or recording player disconnects
            elif event == "[Behaviour] OnPlayerLeft " or event == "[Behaviour] OnPlayerLeftRoom" or event ==  "[Player] OnApplicationQuit":
                if user_sessions and user_sessions[-1]["end"] is None:
                    #if abs(timestamp - user_sessions[-1]["start"]) < duplicate_threshold:
                    user_sessions[-1]["end"] = timestamp
                    #user_sessions[-1]["end"] = timestamp
    now = int(datetime.datetime.now().timestamp())
    for user_data in sessions_by_user.values():
        for session in user_data["sessions"]:
            if session["end"] is None:
                session["end"] = now
    return sessions_by_user
