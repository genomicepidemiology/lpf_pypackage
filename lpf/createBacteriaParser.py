import logging
import os
import json
import sys
import lpf.util.md5 as md5
import pyfastx

import lpf.sqlCommands as sqlCommands
import lpf.util.kmaUtils as kmaUtils
from lpf.kmaRunner import KMARunner
from lpf.util.assemblyUtils import flye_assembly, run_quast, run_bandage
import lpf.pdfReport as pdfReport
import lpf.util.preparePDF as preparePDF

from lpf.loggingHandlers import begin_logging
import lpf.util.mlst as mlst

from lpf.version import __version__

class EmptyDataObject:
    pass

class BacteriaParser():
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
        self.data.bacteria_db = "/opt/lpf_databases/bacteria_db/bacteria_db"
        self.data.resfinder_db = '/opt/lpf_databases/resfinder_db/resfinder_db'
        self.data.plasmidfinder_db = '/opt/lpf_databases/plasmidfinder_db/plasmidfinder_db'
        self.data.virulencefinder_db = '/opt/lpf_databases/virulencefinder_db/virulencefinder_db'
        self.data.mlst_db = '/opt/lpf_databases/mlst_db'
        self.data.sql_db = '/opt/lpf_databases/lpf.db'
        self.data.target_dir = "/opt/lpf_analyses/{}".format(self.data.entry_id)
        self.data.version = __version__
        self.data.black_list = ['62b06be200d3967db6b0f6023d7b5b2e', 'fac82762aa980d285edbbcd45ce952fb'] #IDs from testfiles to be excluded from SQL and reference indexing
        self.logger.info('BacteriaParser initialized with data: {}'.format(self.data.__dict__))
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
        self.logger.info("Total bases in reads: {}. A minimum of 25.000.000 is required.".format(total_bases))
        if total_bases < 25 * 10 ^ 6:
            self.logger.info("Not enough DNA for analysis")
            sys.exit(1)
        else:
            self.logger.info("Enough DNA for analysis. Total bases: {}".format(total_bases))

    def mkfs(self):
        """Creates the target directory and the log file"""
        if not os.path.exists(self.data.target_dir):
            os.makedirs(self.data.target_dir)
            os.makedirs(self.data.target_dir + "/finders")
        else:
            self.logger.info("Target directory already exists. Sample has been analysed before. Exiting.")
            #Consider not existing but just rerunning the analysis
            sys.exit(1)

    def get_reference_mapping_results(self):
        """Returns the mapping results from the reference mapping"""
        if os.path.exists(self.data.target_dir + "/reference_mapping.res"):
            template_score = 0
            reference_header_text = ""
            with open(self.data.target_dir + "/reference_mapping.res", 'r') as f:
                data = f.read().split("\n")
            data = data[:-1] #Last line is empty
            for item in data:
                item = item.split("\t")
                if item[0][0] != "#":
                    if float(item[1]) > template_score:
                        template_score = float(item[1])
                        reference_header_text = item[0]
            template_number = kmaUtils.findTemplateNumber(reference_header_text, '/opt/lpf_databases/bacteria_db/bacteria_db')
            self.data.template_number = template_number
            self.data.template_score = template_score
            self.data.reference_header_text = reference_header_text
            if self.data.template_number != None:
                self.data.reference_id = sqlCommands.sql_fetch_one("SELECT entry_id FROM sequence_table WHERE header = '{}'"
                              .format(self.data.reference_header_text), self.data.sql_db)[0]
                self.logger.info("Reference mapping results: Template number: {}. Template score: {}. Reference header: {}. Reference ID: {}".format(self.data.template_number, self.data.template_score, self.data.reference_header_text, self.data.reference_id))


    def get_mlst_type(self):
        """Returns the mlst results"""
        if not os.path.exists(self.data.target_dir + "/finders/mlst/{}.res".format(self.data.sample_name)):
            self.data.mlst_genes = None
            self.data.mlst_type = None
            self.logger.info("Kmergenetyper didn't produce any results. Skipping MLST analysis")
        else:
            if self.data.mlst_species != None:
                self.data.mlst_genes, self.data.mlst_genes_depths = kmaUtils.parse_kma_res_and_depth('{}/finders/mlst/{}.res'.format(self.data.target_dir, self.data.sample_name))
                self.data.mlst_type, self.data.expected_genes, self.data.st_included_mlst_genes = mlst.derive_mlst(self.data.mlst_species, self.data.mlst_genes, self.data.mlst_genes_depths)
            else:
                self.data.mlst_genes = None
                self.data.expected_genes = None
                self.data.mlst_type = None
                self.data.st_included_mlst_genes = None

    def parse_finder_results(self):
        """Parses the results from the finders"""
        self.logger.info("Parsing results from finders")
        kmaUtils.parse_finders(self)

    def run_assembly(self):
        """
        Performing Flye assebly
        """
        self.logger.info('Performing Flye assebly')
        sqlCommands.sql_update_status_table('Performing assembly', self.data.sample_name, '7', self.data.entry_id, self.data.sql_db)

        flye_assembly(self)
        #TBD medaka

        sqlCommands.sql_update_status_table('Assembly completed', self.data.sample_name, '8', self.data.entry_id, self.data.sql_db)

        self.logger.info('Flye assembly completed')

        run_quast(self)

        self.logger.info('Quast completed')

        run_bandage(self)

        self.logger.info('Bandage completed')

        preparePDF.prepare_assembly_pdf(self)

        self.logger.info('Assembly PDF prepared')

        pdfReport.compile_assembly_report(self)

        self.logger.info('Assembly report compiled')

        sqlCommands.sql_update_status_table('Assembly report compiled', self.data.sample_name, '9', self.data.entry_id, self.data.sql_db)

        sqlCommands.sql_update_status_table('Analysis completed', self.data.sample_name, '10', self.data.entry_id, self.data.sql_db)
        sys.exit(0)

    def single_template_alignment_bacteria(self):
        self.logger.info("Running single template alignment for bacteria")
        template_alignment = KMARunner(self.data.input_path,
                                          self.data.target_dir + "/" + self.data.sample_name,
                                          self.data.bacteria_db,
                                          "-mint3 -Mt1 {} -t 8".format(self.data.template_number))
        template_alignment.run()

        if os.path.exists(self.data.target_dir + "/" + self.data.sample_name + '.fsa'):
            self.logger.info("Single template alignment completed")
            self.data.consensus_sequence_path = self.data.target_dir + "/" + self.data.sample_name + '.fsa'
            header = ''
            sequence = ''
            with open(self.data.consensus_sequence_path, 'r') as f:
                for line in f:
                    if line[0] == '>':
                        header = line[1:].strip()
                    else:
                        sequence += line.strip()
            if header != '' and sequence != '':
                sqlCommands.sql_execute_command("INSERT INTO sequence_table(entry_id, header, sequence) VALUES('{}', '{}', '{}')".format(self.data.entry_id, header, sequence), '/opt/lpf_databases/lpf.db')
                self.insert_isolate_into_cluster_sql()
            else:
                self.logger.info("No consensus sequence found")
        else:
            self.logger.info("No consensus sequence found")

        #handle consensus path
        #Insert consesus into SQL?

    def get_list_of_isolates(self):
        """Returns a list of isolates from the reference template"""
        self.logger.info("Getting list of isolates from reference template")
        self.data.isolate_list = sqlCommands.sql_fetch_all("SELECT entry_id FROM sample_table WHERE reference_id = \"{}\"".format(self.data.reference_id), '/opt/lpf_databases/lpf.db')

    def insert_isolate_into_cluster_sql(self):
        """Inserts the isolate into the cluster SQL database"""
        self.logger.info("Inserting isolate into the identified cluster of {}".format(self.data.reference_header_text))
        sqlCommands.sql_execute_command("UPDATE sample_table SET reference_id = \"{}\" WHERE entry_id = \"{}\"".format(self.data.reference_id, self.data.entry_id), self.data.sql_db)

