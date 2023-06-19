import sys
import logging
def derive_mlst_species(reference_header_text):
    specie = reference_header_text.split(' ')[1] + ' ' + reference_header_text.split(' ')[2]
    mlst_species = reference_header_text.split(' ')[1][0].lower() + reference_header_text.split(' ')[2].lower()
    with open("/opt/lpf_databases/mlst_db/config", 'r') as infile:
        for line in infile:
            if line[0] != "#":
                line = line.split("\t")
                if mlst_species == line[0]:
                    return specie, mlst_species
    return specie, None

def check_muliple_alelles(found_genes, expected_genes):
    flag = False
    hits = set()
    multiples = set()
    mlst_genes = set()
    for item in found_genes:
        gene = item.split("_")[0]
        if gene in expected_genes:
            if gene not in hits:
                hits.add(gene)
                mlst_genes.add(item)
            else:
                flag = True
                multiples.add(gene)
    if len(hits) == len(expected_genes):
        return flag, multiples, True, mlst_genes
    return flag, multiples, False, mlst_genes

def look_up_mlst(file, mlst_genes, expected_genes):
    if len(mlst_genes) != len(expected_genes):
        return "Not all alleles were found"
    with open(file, 'r') as infile:
        for line in infile:
            if not line.startswith('ST'):
                line = line.rstrip().split("\t")
                potential_mlst_set = set()
                for i in range(len(expected_genes)):
                    potential_mlst_set.add(expected_genes[i] + "_" + line[i + 1])
                if potential_mlst_set == mlst_genes:
                    return line[0]
    return "Unknown ST"


def select_highest_depth_alleles(found_genes, template_depth, expected_genes, multiple_allele_list):
    final_genes = set()
    for i in range(len(template_depth)):
        gene = found_genes[i].split("_")[0]
        if gene not in multiple_allele_list and gene in expected_genes:
            final_genes.add(found_genes[i])

    for item in multiple_allele_list:
        high_score = 0
        name = ''
        for i in range(len(found_genes)):
            if found_genes[i].startswith(item):
                if float(template_depth[i]) > high_score:
                    high_score = float(template_depth[i])
                    name = found_genes[i]
        final_genes.add(name)
    return final_genes

def derive_mlst(species, found_genes, template_depth):
    """Returns the mlst results"""
    with open("/opt/lpf_databases/mlst_db/config", 'r') as fd:
        for line in fd:
            if line[0] != "#":
                line = line.rstrip().split("\t")
                if line[0] == species:
                    expected_genes = line[2].split(",")
    multiple_alelles, multiple_allele_list, mlst_bool, mlst_genes = check_muliple_alelles(found_genes, expected_genes)

    if mlst_bool:
        if multiple_alelles:
            #Simply selecting highest depth hits but gives warning!
            if template_depth != 'skip':
                mlst_genes = select_highest_depth_alleles(found_genes, template_depth, expected_genes, multiple_allele_list)
            mlst_type = look_up_mlst("/opt/lpf_databases/mlst_db/{0}/{0}.tsv".format(species), mlst_genes, expected_genes)
            mlst_type += '+'
        else:
            mlst_type = look_up_mlst("/opt/lpf_databases/mlst_db/{0}/{0}.tsv".format(species), mlst_genes, expected_genes)
        if not check_allele_template_coverage:
            mlst_type += '*'
        return mlst_type, expected_genes, list(mlst_genes)
    else:
        return 'Unknown ST', expected_genes, []


def check_allele_template_coverage(mlst_genes, template_depth, found_genes):
    """
    Checks if the allele depth is above 100 else returns false
    :param mlst_genes:
    :param template_depth:
    :param found_genes:
    :return:
    """
    flag = True
    for i in range(len(found_genes)):
        if found_genes[i] in mlst_genes:
            if template_depth[i] < 100:
                flag = False
    return flag