from unittest import TestCase
import src.lpf_functions as lpf
from src.lpf import lpfObject
import json
import os
import inspect

class TestSetUpFunctions(TestCase):
    def setUp(self):
        with open('tests/fixtures/json/assembly_test.json') as json_file:
            test_json = json.load(json_file)['samples'][0]
        self.input_dict = lpfObject(test_json)
        print (inspect(getmembers(self.input_dict)))


    def test_lpf_init(self):
        self.input_dict = lpf.lpf_init(self.input_dict)
        self.assertEqual(self.input_dict['entry_id'] is not None, True)
        self.assertEqual(self.input_dict['lpf_db'] is not None, True)
        self.assertEqual(self.input_dict['sample_name'] is not None, True)
        self.assertEqual(self.input_dict['ref_db'] is not None, True)
        self.assertEqual(self.input_dict['target_dir'] is not None, True)
class TestLeftOvers(TestCase):
    def setUp(self):
        with open('tests/fixtures/json/assembly_test.json') as json_file:
            test_json = json.load(json_file)['samples'][0]
        self.input_dict = lpf.lpf_init(test_json)

    def test_create_directory_from_dict(self):
        self.assertEqual(True, True) #Placeholder

    def test_lpf_mkfs(self):
        self.assertEqual(True, True)

class TestParseFunctions(TestCase):
    def setUp(self):
        with open('tests/fixtures/json/assembly_test.json') as json_file:
            test_json = json.load(json_file)['samples'][0]
        self.input_dict = lpf.lpf_init(test_json)
        self.input_dict['target_dir'] = 'tests/fixtures/'

    def test_parse_finders_pass(self):
        self.input_dict = lpf.parse_finders(self.input_dict)
        print (self.input_dict)
        self.assertEqual(self.input_dict['virulence_hits'][0], 'gad:31:CP002967')
        self.assertEqual(self.input_dict['resfinder_hits'][0], 'blaOXA-181_1_CM004561')
        self.assertEqual(self.input_dict['plasmid_hits'][0], 'IncFIA_1__AP001918')
        #mlst missing

    def test_parse_kma_res_pass(self):
        self.plasmid_list = lpf.parse_kma_res('tests/fixtures/finders/plasmidfinder.res')
        print (self.plasmid_list)


class TestQcCheck(TestCase):
    def setUp(self):
        with open('tests/fixtures/json/assembly_test.json') as json_file:
            test_json = json.load(json_file)['samples'][0]
        self.input_dict = lpf.lpf_init(test_json)

    def test_qc_check_pass(self):
        self.assertTrue(lpf.qc_check(self.input_dict), 'Input QC check showed below 3MB file size')

    def test_qc_check_fail(self):
        self.input_dict['input_path'] = 'tests/fixtures/mlstresults/kma_ecoli_alignment_test.res'
        self.assertRaises(SystemExit, lpf.qc_check, self.input_dict) #Consider using other file

class TestSqlCommands(TestCase):
    def setUp(self):
        with open('tests/fixtures/json/assembly_test.json') as json_file:
            test_json = json.load(json_file)['samples'][0]
        self.input_dict = lpf.lpf_init(test_json)
        self.input_dict['lpf_db'] = 'tests/fixtures/database/lpf.db'
        lpf.create_sql_db('tests/fixtures/database/', 'datafiles/bacteria_metadata.json')

    def tearDown(self):
        os.system("rm -rf tests/fixtures/database/lpf.db")

    def test_sql_execute_command_pass(self):
        entry_id = lpf.md5_of_file(self.input_dict['input_path'])
        lpf.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                .format(entry_id, self.input_dict['sample_name'], "Queued", "Queued", "Queued",
                        "Queued", "Queued", ""), 'tests/fixtures/database/lpf.db')
        result = lpf.sql_fetch_one("SELECT result FROM status_table WHERE entry_id = '{}'".format(entry_id),
                                    self.input_dict['lpf_db'])
        self.assertEqual(len(result), 1)
    def test_sql_fetch_one(self):
        entry_id = lpf.md5_of_file(self.input_dict['input_path'])
        lpf.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                .format(entry_id, self.input_dict['sample_name'], "Queued", "Queued", "Queued",
                        "Queued", "Queued", ""), 'tests/fixtures/database/lpf.db')
        result = lpf.sql_fetch_one("SELECT result FROM status_table WHERE entry_id = '{}'".format(entry_id),
                                    self.input_dict['lpf_db'])
        self.assertEqual(len(result), 1)
        lpf.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                .format('test1', self.input_dict['sample_name'], "Queued", "Queued", "Queued",
                        "Queued", "Queued", ""), 'tests/fixtures/database/lpf.db')
        result = lpf.sql_fetch_one("SELECT result FROM status_table WHERE entry_id = '{}'".format('test1'),
                                    self.input_dict['lpf_db'])
        self.assertEqual(len(result), 1)

    def test_sql_fetch_all(self):
        entry_id = lpf.md5_of_file(self.input_dict['input_path'])
        lpf.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                .format(entry_id, self.input_dict['sample_name'], "Queued", "Queued", "Queued",
                        "Queued", "Queued", ""), 'tests/fixtures/database/lpf.db')
        result = lpf.sql_fetch_all("SELECT entry_id FROM status_table WHERE result = '{}'".format('Queued'),
                                    self.input_dict['lpf_db'])
        self.assertEqual(len(result), 1)
        lpf.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                .format('test1', self.input_dict['sample_name'], "Queued", "Queued", "Queued",
                        "Queued", "Queued", ""), 'tests/fixtures/database/lpf.db')
        result = lpf.sql_fetch_all("SELECT entry_id FROM status_table WHERE result = '{}'".format('Queued'),
                                    self.input_dict['lpf_db'])
        print (result)
        self.assertEqual(len(result), 2)

    def test_completed_run_update_sql_database_assembly_hp(self):
        entry_id = lpf.md5_of_file(self.input_dict['input_path'])
        lpf.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                .format(entry_id, self.input_dict['sample_name'], "Queued", "Queued", "Queued",
                        "Queued", "Queued", ""), 'tests/fixtures/database/lpf.db')
        lpf.completed_run_update_sql_database('assembly', self.input_dict)
        result = lpf.sql_fetch_one("SELECT status FROM status_table WHERE entry_id = '{}'".format(entry_id), self.input_dict['lpf_db'])[0]
        self.assertEqual(result, 'Completed')

    def test_completed_run_update_sql_database_alignment_hp(self):
        entry_id = lpf.md5_of_file(self.input_dict['input_path'])
        lpf.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                .format(entry_id, self.input_dict['sample_name'], "Queued", "Queuedqc_check", "Queued",
                        "Queued", "Queued", ""), 'tests/fixtures/database/lpf.db')
        lpf.completed_run_update_sql_database('alignment', self.input_dict)
        result = lpf.sql_fetch_one("SELECT status FROM status_table WHERE entry_id = '{}'".format(entry_id), self.input_dict['lpf_db'])[0]
        self.assertEqual(result, 'Completed')

    def test_clean_sql_for_lpf_run(self):
        entry_id = lpf.md5_of_file(self.input_dict['input_path'])
        lpf.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                .format(entry_id, self.input_dict['sample_name'], "Queued", "Queued", "Queued",
                        "Queued", "Queued", ""), 'tests/fixtures/database/lpf.db')
        lpf.sql_execute_command(lpf.clean_sql_for_lpf_run(self.input_dict), 'tests/fixtures/database/lpf.db')
        result = lpf.sql_fetch_one("SELECT status FROM status_table WHERE entry_id = '{}'"
                      .format(entry_id), self.input_dict['lpf_db'])[0]
        self.assertEqual(result, 'Run failed')

    def test_create_sql_db(self):
        self.assertTrue(os.path.exists('tests/fixtures/database/lpf.db'), 'create_sql_db did not create a database')

class TestValidateDateText(TestCase):
    def setUp(self):
        self.hp_date_time = '1996-06-01'
        self.sp_date_time = '01-06-1996'

    def test_hp_date_time(self):
        self.assertEqual(None, lpf.validate_date_text(self.hp_date_time))

    def test_sp_date_time(self):
        self.assertRaises(ValueError, lpf.validate_date_text, self.sp_date_time)


class TestValidateInput(TestCase):
    def setUp(self):
        with open('tests/fixtures/json/assembly_test.json') as json_file:
            self.test_json = json.load(json_file)['samples'][0]

    def test_sp_input_path(self):
        self.test_json['input_path'] = '/opt/lpf_data/test_dir/file.fastq.gzsadgasd'
        self.assertRaises(SystemExit, lpf.validate_lpf_object, self.test_json)

    def test_hp_all(self):
        self.assertEqual(None, lpf.validate_lpf_object(self.test_json))

    def test_bad_path_collection_date(self):
        self.test_json['collection_date'] = '07/12/1984'
        with self.assertRaises(ValueError):
            lpf.validate_lpf_object(self.test_json)
