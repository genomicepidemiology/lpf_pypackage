import os
import sys
import datetime
from fpdf import FPDF
import dataframe_image as dfi
import pandas as pd
import json
import csv
def prepare_alignment_pdf(bacteria_parser):
    if not os.path.exists(bacteria_parser.data.target_dir + "/pdf_resources"):
        os.mkdir(bacteria_parser.data.target_dir + "/pdf_resources")
    file_list = ["/opt/lpf_databases/resfinder_db/phenotypes.txt",
                 "/opt/lpf_databases/virulencefinder_db/notes.txt",
                 ]
    for item in file_list:
        if not os.path.exists(item):
            bacteria_parser.logger.info("File {} does not exist. Could not compile assembly".format(file))
            sys.exit(1)
    make_amr_csv(bacteria_parser)
    make_virulence_csv(bacteria_parser)
    make_plasmid_csv(bacteria_parser)
    output_bacteria_parser(bacteria_parser)

def make_amr_csv(bacteria_parser): #TBD rewrite and remove.
    phenotype = dict()
    infile = open("/opt/lpf_databases/resfinder_db/phenotypes.txt", 'r')
    for line in infile:
        if not line.startswith("Gene_accession"):
            line = line.rstrip().split("\t")
            if line[0] in bacteria_parser.data.resfinder_hits:
                phenotype[line[0]] = [line[1], line[2]]
    csv_data = []
    csv_data.append(("Gene", "Resistance Class", "Phenotype"))
    for item in phenotype:
        csv_data.append([item, phenotype[item][0], phenotype[item][1]])
    with open(bacteria_parser.data.target_dir + "/pdf_resources/amr_data.csv", 'w') as f:
        for item in csv_data:
            print (",".join(item), file=f)


def make_virulence_csv(bacteria_parser):  #TBD rewrite and remove.
    new_genes = list()
    for item in bacteria_parser.data.virulence_hits:
        new_genes.append(item.split(":")[0])
    genes = new_genes
    phenotype = dict()
    infile = open("/opt/lpf_databases/virulencefinder_db/notes.txt", 'r')
    for line in infile:
        if line[0] != "#":
            line = line.rstrip().split(":")
            if line[0] in genes:
                if line[1] in phenotype:
                    phenotype[line[1].strip()].append(line[0])
                else:
                    phenotype[line[1].strip()] = [line[0]]

    csv_data = []
    csv_data.append(("Virulence", "Genes"))
    for item in phenotype:
        csv_data.append((item, ", ".join(phenotype[item])))
    with open(bacteria_parser.data.target_dir + "/pdf_resources/virulence_data.csv", 'w') as f:
        for item in csv_data:
            print (",".join(item), file=f)

def output_bacteria_parser(bacteria_parser):
    with open(bacteria_parser.data.target_dir + "/pdf_resources/bacteria_parser.json", 'w') as f:
        json.dump(bacteria_parser.data.__dict__, f, indent=4)

def make_plasmid_csv(bacteria_parser):
    csv_data = []
    csv_data.append(("Plasmids"))
    for item in bacteria_parser.data.plasmid_hits:
        csv_data.append((item))
    with open(bacteria_parser.data.target_dir + "/pdf_resources/plasmid_data.csv", 'w') as f:
        for item in csv_data:
            print (item, file=f)

def prepare_assembly_pdf(bacteria_parser):
    if not os.path.exists(bacteria_parser.data.target_dir + "/pdf_resources"):
        os.mkdir(bacteria_parser.data.target_dir + "/pdf_resources")
    file_list = ["/opt/lpf_databases/resfinder_db/phenotypes.txt",
                 "/opt/lpf_databases/virulencefinder_db/notes.txt",
                 bacteria_parser.data.target_dir + "/quast_output/report.tsv"
                 ]
    for file in file_list:
        if not os.path.exists(file):
            bacteria_parser.logger.info("File {} does not exist. Could not compile assembly".format(file))
            sys.exit(1)

    csv_data = []
    with open(bacteria_parser.data.target_dir + "/quast_output/report.tsv", 'r') as f:
        for line in f:
            csv_data.append(line.rstrip().split("\t"))
            
    with open(bacteria_parser.data.target_dir + "/pdf_resources/quast_report.csv", 'w') as f:
        for item in csv_data:
            print (",".join(item), file=f)

    make_amr_csv(bacteria_parser)
    make_virulence_csv(bacteria_parser)
    make_plasmid_csv(bacteria_parser)
    output_bacteria_parser(bacteria_parser)
