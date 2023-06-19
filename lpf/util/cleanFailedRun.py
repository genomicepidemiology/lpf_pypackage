import os
import lpf.sqlCommands as sqlCommands
import json
import lpf.util.md5 as md5

class EmptyDataObject:
    pass
def clean_failed_run(input_json):
    """Clean up failed run"""

    with open(input_json, 'r') as f:
        data_dict = json.loads(f.read())
    data = EmptyDataObject()
    for item in data_dict:
        setattr(data, item, data_dict[item])
    data.entry_id = md5.md5_of_file(data.input_path)
    sqlCommands.sql_update_status_table('Analysis failed', data.input_file, 'Failed, log info in /opt/lpf_logs', data.entry_id, '/opt/lpf_databases/lpf.db')