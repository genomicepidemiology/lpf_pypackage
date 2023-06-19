"""Wrapper for running multiple analysis. Currently, parallel analysis is not enabled."""
import sys
import os
import argparse
import util.md5 as md5
from joblib import Parallel, delayed
import sqlCommands as sqlCommands
import datetime
import json

parser = argparse.ArgumentParser(description='.')
parser.add_argument('-info', type=int, help='surveillance info')
parser.add_argument('-batch_json', action="store", type=str, dest='batch_json', default="",
                    help='batch json file')
parser.add_argument('-analysis_type', action="store",
                                 type=str, dest='analysis_type', default="bacteria",
                                 help='bacteria, virus or metagenomic')
args = parser.parse_args()

def lpf_analysis(jobslist, i):
    """Start analysis"""
    try:
        os.system(jobslist[i])
    except Exception as e:
        sys.exit("LocalPathogenFinder: Error: {}. lpf was NOT run.".format(e))

def main(analysis_type, batch_json):
    """Main func"""
    json_list = create_individual_json_files(batch_json)
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

        if os.path.exists('/opt/lpf/bin/LocalPathogenFinder'):
            cmd = 'python3 /opt/lpf/bin/LocalPathogenFinder {} -json {}'.format(analysis_type, item)
        else:
            cmd = 'python3 LocalPathogenFinder {} -json {}'.format(analysis_type, item)
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

if __name__== "__main__":
    main(args.analysis_type, args.batch_json)
