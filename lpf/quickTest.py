import os
import sys

import argparse

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')] + sys.path

from batchStarter import batch_starter

import lpf.sqlCommands as sqlCommands


def clean_up(md5_list):
    for item in md5_list:
        os.system("rm -rf /opt/lpf_logs/{}.log".format(item))
        os.system("rm -rf /opt/lpf_analyses/{}".format(item))
        sqlCommands.sql_execute_command('DELETE FROM status_table WHERE entry_id = \"{}\"'.format(item), '/opt/lpf_databases/lpf.db')
        sqlCommands.sql_execute_command('DELETE FROM meta_data_table WHERE entry_id = \"{}\"'.format(item), '/opt/lpf_databases/lpf.db')
        sqlCommands.sql_execute_command('DELETE FROM sample_table WHERE entry_id = \"{}\"'.format(item), '/opt/lpf_databases/lpf.db')
        sqlCommands.sql_execute_command('DELETE FROM sequence_table WHERE entry_id = \"{}\"'.format(item), '/opt/lpf_databases/lpf.db')

def quick_test():
    if not os.path.exists('/opt/lpf_test_data'):
        sys.exit('Quick test data does not exists on this system.')
    md5_list = ['62b06be200d3967db6b0f6023d7b5b2e', 'fac82762aa980d285edbbcd45ce952fb', '83d1531bdc862f7ddbf754221fae6a66', 'e919efc7e3f8906bb47d99f85478d1d5']
    clean_up(md5_list)
    batch_starter('bacteria', '/opt//lpf_test_data/fixtures/json/bac1.json')
    batch_starter('bacteria', '/opt//lpf_test_data/fixtures/json/bac2.json')
    batch_starter('virus', '/opt//lpf_test_data/fixtures/json/virus1.json')
    batch_starter('virus', '/opt//lpf_test_data/fixtures/json/virus2.json')