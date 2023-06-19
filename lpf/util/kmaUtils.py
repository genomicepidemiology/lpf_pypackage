import os

def findTemplateNumber(name, database):
    if os.path.exists(database + ".name"):
        with open(database + ".name") as f:
            t = 1
            for line in f:
                if line.rstrip().startswith(name):
                    return t
                else:
                    t += 1
                    
def parse_finders(bacteria_parser):
    bacteria_parser.data.resfinder_hits = parse_kma_res("{}/finders/resfinder_mapping.res".format(bacteria_parser.data.target_dir))
    bacteria_parser.data.virulence_hits = parse_kma_res("{}/finders/virulencefinder_mapping.res".format(bacteria_parser.data.target_dir))
    bacteria_parser.data.plasmid_hits = parse_kma_res("{}/finders/plasmidfinder_mapping.res".format(bacteria_parser.data.target_dir))

def parse_kma_res(filename):
    item_list = list()
    infile = open(filename, 'r')
    for line in infile:
        if line[0] != "#":
            line = line.split('\t')
            item_list.append(line[0])
    return item_list

def parse_kma_res_and_depth(file):
    genes = []
    template_depth = []
    with open('file', 'r') as f:
        for line in f:
            if not line.startswith('#'):
                genes.append(line.strip().split('\t')[0])
                template_depth.append(line.strip().split('\t')[-3])
    return genes, template_depth

def parse_kma_res_to_list_of_lists(filename):
    item_list = list()
    with open(filename, 'r') as f:
        for line in f:
            inner_list = list()
            line = line.rstrip()
            if line[0] != "#":
                line = line.split('\t')
                inner_list.append(line[0])
                inner_list.append(line[3])
                inner_list.append(line[4])
                inner_list.append(line[8])
                item_list.append(inner_list)
    return item_list


def get_reference_mapping_results(file, database):
    """Returns the mapping results from the reference mapping"""
    if os.path.exists(file):
        template_score = 0
        reference_header_text = ""
        with open(file, 'r') as f:
            data = f.read().split("\n")
        data = data[:-1] #Last line is empty
        for item in data:
            item = item.split("\t")
            if item[0][0] != "#":
                if float(item[1]) > template_score:
                    template_score = float(item[1])
                    reference_header_text = item[0]
        template_number = findTemplateNumber(reference_header_text, database)
        return template_number, template_score, reference_header_text