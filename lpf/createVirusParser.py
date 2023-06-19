import logging
import os
import json
import sys
import lpf.util.md5 as md5
import pyfastx

import lpf.util.kmaUtils as kmaUtils

from lpf.loggingHandlers import begin_logging

from lpf.version import __version__

class EmptyDataObject:
    pass

class VirusParser():
    def __init__(self, file):
        with open(file, 'r') as f:
            data_dict = json.loads(f.read())
        self.data = EmptyDataObject()
        for item in data_dict:
            setattr(self.data, item, data_dict[item])
        self.data.entry_id = md5.md5_of_file(self.data.input_path)
        begin_logging('/opt/lpf_logs/{}.log'.format(self.data.entry_id))
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.info("Starting analysis of {}".format(self.data.entry_id))
        self.data.sample_name = os.path.basename(self.data.input_path).split('.')[0]
        self.data.sql_db = '/opt/lpf_databases/lpf.db'
        self.data.virus_db = '/opt/lpf_databases/virus_db/virus_db'
        self.data.cdd_db = '/opt/lpf_databases/cdd_db/cdd_db'
        self.data.target_dir = "/opt/lpf_analyses/{}".format(self.data.entry_id)
        self.data.version = __version__
        self.data.black_list = ['62b06be200d3967db6b0f6023d7b5b2e', 'fac82762aa980d285edbbcd45ce952fb'] #IDs from testfiles to be excluded from SQL and reference indexing
        self.logger.info('VirusParser initialized with data: {}'.format(self.data.__dict__))
        self.qc_check()
        self.mkfs()

    def __str__(self):
        return str(self.data.__dict__)

    def __repr__(self):
        return self.data.__dict__

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        return self.data[key]
    def qc_check(self):
        """Very basic QC. Only checks for a minimum amount of input data for bacteria analysis"""
        fq = pyfastx.Fastq(self.data.input_path, build_index=False)
        total_bases = 0
        for read in fq:
            total_bases += len(read[1])
        self.logger.info("Total bases in reads: {}. A minimum of 250.000 is required.".format(total_bases))
        if total_bases < 25 * 10 ^ 4:
            self.logger.info("Not enough DNA for analysis")
            sys.exit(1)
        else:
            self.logger.info("Enough DNA for analysis. Total bases: {}".format(total_bases))

    def mkfs(self):
        """Creates the target directory and the log file"""
        if not os.path.exists(self.data.target_dir):
            os.makedirs(self.data.target_dir)
        else:
            self.logger.info("Target directory already exists. Sample has been analysed before. Exiting.")
            #Consider not existing but just rerunning the analysis
            sys.exit(1)


    def parse_virus_results(self):
        """Parses virus analysis results"""
        self.logger.info("Parsing results from virus analysis")
        if not os.stat(self.data.target_dir + '/cdd_alignment.fsa').st_size == 0:
            self.data.cdd_hits = kmaUtils.parse_kma_res_to_list_of_lists(self.data.target_dir + '/cdd_alignment.res')
        else:
            self.data.cdd_hits = None
        if not os.stat(self.data.target_dir + '/virus_alignment.fsa').st_size == 0:
            self.data.virus_hits = kmaUtils.parse_kma_res(self.data.target_dir + '/virus_alignment.res')
            self.data.template_number, self.data.template_score, self.data.reference_header_text = kmaUtils.get_reference_mapping_results(self.data.target_dir + '/virus_alignment.res', self.data.virus_db)
        else:
            self.data.virus_hits = None
            self.data.template_number = None
            self.data.template_score = None
            self.data.reference_header_text = None
        if os.path.exists(self.data.target_dir + '/virus_assembly.fsa'):
            #Change reference_header_text
            pass
        if os.path.exists(self.data.target_dir + '/prokka_output/prokka_results.tsv'):
            if not os.stat(self.data.target_dir + '/prokka_output/prokka_results.tsv').st_size == 0:
                prokka_tsv_list = []
                with open(self.data.target_dir + '/prokka_output/prokka_results.tsv', 'r') as f:
                    for line in f:
                        prokka_tsv_list.append(line.strip().split('\t'))
                self.data.prokka_tsv_list = prokka_tsv_list
        else:
            self.data.prokka_tsv_list = None



