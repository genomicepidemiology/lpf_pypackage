import os
import sys

import argparse

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')] + sys.path

import lpf.sqlCommands as sqlCommands


def clean_up(md5_list):
    for item in md5_list:
        os.system("rm -rf /opt/lpf_logs/{}.log".format(item))
        os.system("rm -rf /opt/lpf_analyses/{}".format(item))
        sqlCommands.sql_execute_command('DELETE FROM status_table WHERE entry_id = \"{}\"'.format(item), '/opt/lpf_databases/lpf.db')
        sqlCommands.sql_execute_command('DELETE FROM meta_data_table WHERE entry_id = \"{}\"'.format(item), '/opt/lpf_databases/lpf.db')
        sqlCommands.sql_execute_command('DELETE FROM sample_table WHERE entry_id = \"{}\"'.format(item), '/opt/lpf_databases/lpf.db')
        sqlCommands.sql_execute_command('DELETE FROM sequence_table WHERE entry_id = \"{}\"'.format(item), '/opt/lpf_databases/lpf.db')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Quick test script')
    parser.add_argument('-virus', action='store_true', help='Run virus test')
    parser.add_argument('-bacteria', action='store_true', help='Run bacteria test')

    args = parser.parse_args()


    md5_list = ['62b06be200d3967db6b0f6023d7b5b2e', 'fac82762aa980d285edbbcd45ce952fb', '83d1531bdc862f7ddbf754221fae6a66', 'e919efc7e3f8906bb47d99f85478d1d5']
    clean_up(md5_list)
    if args.virus:
        os.system('python3 /opt/lpf/lpf/batchStarter.py -analysis_type virus -batch_json /opt/lpf/tests/fixtures/virus_batch.json')
        sys.exit()
    if args.bacteria:
        os.system('python3 /opt/lpf/lpf/batchStarter.py -analysis_type bacteria -batch_json /opt/lpf/tests/fixtures/bacteria_batch.json')
        sys.exit()
    os.system('python3 /opt/lpf/lpf/batchStarter.py -analysis_type bacteria -batch_json /opt/lpf/tests/fixtures/bacteria_batch.json')
    os.system('python3 /opt/lpf/lpf/batchStarter.py -analysis_type virus -batch_json /opt/lpf/tests/fixtures/virus_batch.json')