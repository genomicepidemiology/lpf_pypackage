###############################################################################
# Pipeline for Virus analysis
###############################################################################
import logging
import os
import sys
import datetime

from lpf.kmaRunner import KMARunner
import lpf.util.ccphyloUtils as ccphyloUtils
import lpf.sqlCommands as sqlCommands
import lpf.pdfReport as pdfReport
import lpf.util.preparePDF as preparePDF
from lpf.kmergenetyperRunner import kmergenetyperRunner
import lpf.util.mlst as mlst
from lpf.prokkaRunner import prokkaRunner
from lpf.localPhylogeny import local_phylogeny_from_input_and_database



def virus_analysis_pipeline(virus_parser):
    """Runs the virus analysis pipeline"""
    sqlCommands.sql_update_status_table('Analysis started', virus_parser.data.sample_name, '1',
                                        virus_parser.data.entry_id, virus_parser.data.sql_db)
    sqlCommands.sql_execute_command("INSERT INTO sample_table(entry_id, sample_type) VALUES('{}', '{}')"
                                    .format(virus_parser.data.entry_id, 'virus'), virus_parser.data.sql_db)
    sqlCommands.sql_update_status_table('Virus alignment', virus_parser.data.sample_name, '2',
                                        virus_parser.data.entry_id, virus_parser.data.sql_db)

    KMARunner(virus_parser.data.input_path,
              virus_parser.data.target_dir + "/virus_alignment",
              virus_parser.data.virus_db,
              "-ont -ca -1t1 -mem_mode").run()

    #Consider identity and perhaps assemble if its bad:

    sqlCommands.sql_update_status_table('CDD alignment', virus_parser.data.sample_name, '3',
                                        virus_parser.data.entry_id, virus_parser.data.sql_db)

    KMARunner(virus_parser.data.input_path,
              virus_parser.data.target_dir + "/cdd_alignment",
              virus_parser.data.cdd_db,
              "-ont -ca -1t1 -mem_mode").run()

    sqlCommands.sql_update_status_table('Prokka annotation', virus_parser.data.sample_name, '2',
                                        virus_parser.data.entry_id, virus_parser.data.sql_db)

    prokkaRunner(virus_parser.data.sample_name,
                 virus_parser.data.target_dir + "/virus_alignment.fsa",
                 virus_parser.data.entry_id,
                 virus_parser.data.target_dir).run()

    #Phylogenetic analysis
    #Pathogenicy prediction

    virus_parser.parse_virus_results()

    sqlCommands.sql_update_status_table('Compiling PDF', virus_parser.data.sample_name, '9', virus_parser.data.entry_id, virus_parser.data.sql_db)

    #local_phylogeny_from_input_and_database(virus_parser.data.input_path, virus_parser.data.virus_db, virus_parser.data.reference_header_text.split(':')[1], virus_parser.data.target_dir)

    pdfReport.compile_virus_report(virus_parser)

    sqlCommands.sql_update_status_table('Analysis completed', virus_parser.data.sample_name, '10', virus_parser.data.entry_id, virus_parser.data.sql_db)

    return 0







