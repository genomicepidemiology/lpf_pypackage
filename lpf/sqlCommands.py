import sqlite3
import datetime

def sql_execute_command(command, database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute(command)
    conn.commit()
    conn.close()

def sql_fetch_all(string, database):
    """ Fetches query results from the database and returns them as a list of tuples"""
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute(string)
    data = c.fetchall()
    data = [item for t in data for item in t]
    conn.close()
    return data

def sql_fetch_one(string, database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute(string)
    data = c.fetchone()
    conn.close()
    return data

def sql_update_status_table(status, input_file, stage, entry_id, database):
    time_stamp = str(datetime.datetime.now())[0:-7]
    sql_cmd = "UPDATE status_table SET status=\"{}\", input_file =\"{}\", time_stamp=\"{}\", stage=\"{}\" WHERE entry_id=\"{}\"".format(status, input_file, time_stamp, stage, entry_id)
    sql_execute_command(sql_cmd, database)