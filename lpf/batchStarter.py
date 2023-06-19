import sys
import os
import datetime
import json

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')] + sys.path

import lpf.util.md5 as md5
from joblib import Parallel, delayed
import lpf.sqlCommands as sqlCommands



def lpf_analysis(jobslist, i):
    """Start analysis"""
    try:
        os.system(jobslist[i])
    except Exception as e:
        sys.exit("LocalPathogenFinder: Error: {}. lpf was NOT run.".format(e))

def batch_starter(analysis_type, batch_json):
    with open(batch_json) as infile:
        data = json.load(infile)
    if 'batch_runs' in data:
        json_list = create_individual_json_files(batch_json)

    else:
        json_list = [batch_json]
    jobslist = []
    for item in json_list:
        data = json.load(open(item))
        input_file = data['input_file']
        entry_id = md5.md5_of_file(data['input_path'])
        time_stamp = str(datetime.datetime.now())[0:-7]
        try:
            sqlCommands.sql_execute_command(
                "INSERT INTO status_table(entry_id, input_file, status, time_stamp, stage) VALUES ('{}', '{}', '{}', '{}', '{}')" \
                    .format(entry_id, input_file, 'Queued, not started', time_stamp, '1'), '/opt/lpf_databases/lpf.db')
        except Exception as e:
            sys.exit("LocalPathogenFinder: Error: {}. lpf was NOT run.".format(e))

        cmd = 'conda run -n lpf {} -json {}'.format(analysis_type, item)
        jobslist.append(cmd)

    Parallel(n_jobs=1)(delayed(lpf_analysis)(jobslist, i) for i in range(len(jobslist))) #Can be changed to parallelize

def create_individual_json_files(batch_json):
    """Create individual json files for each sample"""
    with open(batch_json) as infile:
        data = json.load(infile)
    output_list = []
    for item in data['batch_runs']:
        entry_id = md5.md5_of_file(item['input_path'])
        with open("/opt/lpf_metadata_json/individual_json/{}.json".format(entry_id), 'w') as outfile:
            json.dump(item, outfile)
        output_list.append("/opt/lpf_metadata_json/individual_json/{}.json".format(entry_id))
    return output_list