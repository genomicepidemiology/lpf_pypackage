import os
import sys
import random

import lpf.util.kmaUtils as kmaUtils

def local_phylogeny_from_input_and_database(input, database, specie, target_dir):
    """Runs local phylogeny from input and database"""
    reference_species = list()
    with open(database + ".name", 'r') as f:
        for line in f:
            if specie in line:
                reference_species.append(line.rstrip().split(' ')[0])
    print (reference_species)
    print (len(reference_species))
    if len(reference_species) == 0:
        return None
    if len(reference_species) > 20:
        reference_species = random.sample(reference_species, 20)
    print (reference_species)
    os.mkdir(target_dir + "/local_phylogeny")
    for item in reference_species:
        print (item, database)
        template_number = kmaUtils.findTemplateNumber(item, database)
        print (template_number)
        print ('kma seq2fasta -t_db {} -seqs {} > {}/local_phylogeny/{}.fasta'.format(database, template_number, target_dir, item.split(':')[0]))
        os.system('kma seq2fasta -t_db {} -seqs {} > {}/local_phylogeny/{}.fasta'.format(database, template_number, target_dir, item.split(':')[0]))

