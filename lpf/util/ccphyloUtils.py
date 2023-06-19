import os
import sys
import subprocess


def ccphylo_dist(bacteria_parser):
    make_ccphylo_folder(bacteria_parser)
    cmd = "~/bin/ccphylo dist --input {0}/phytree_output/* --reference \"{1}\" --min_cov 0.01" \
          " --normalization_weight 0 --output {0}/phytree_output/distance_matrix" \
        .format(bacteria_parser.data.target_dir, bacteria_parser.data.reference_header_text)

    proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    err = proc.communicate()[1].decode().rstrip().split(" ")
    bacteria_parser.logger.info(proc.communicate()[1].decode().rstrip())
    try:
        inclusion_fraction = int(err[3])/int(err[5])
        bacteria_parser.logger.info("Inclusion fraction: {}".format(inclusion_fraction))
    except:
        inclusion_fraction = None
        bacteria_parser.logger.info("Inclusion fraction was not calculated.")
    distance = ThreshholdDistanceCheck(bacteria_parser)
    bacteria_parser.logger.info("Input consensus sequence distance from reference: {}".format(distance))
    return inclusion_fraction, distance

def ThreshholdDistanceCheck(bacteria_parser):
    if not os.path.exists(bacteria_parser.data.target_dir + '/phytree_output/distance_matrix'):
        bacteria_parser.logger.info('ERROR: Distance matrix was not created.')
    infile = open(bacteria_parser.data.target_dir + '/phytree_output/distance_matrix', 'r')
    consensus_name = bacteria_parser.data.sample_name + '.fsa'
    header_name = bacteria_parser.data.reference_header_text.split()[0] + '.fsa'
    linecount = 0
    secondentry = False
    for line in infile:
        line = line.rstrip()
        line = line.split("\t")
        if secondentry == True:
            if line[0] == consensus_name or line[0] == header_name:
                distance = line[linecount-1]
                return float(distance)
        if secondentry == False:
            if line[0] == consensus_name or line[0] == header_name:
                index = linecount
                secondentry = True
        linecount += 1
    return None

def make_ccphylo_folder(bacteria_parser):
    cmd = "mkdir {}/phytree_output".format(bacteria_parser.data.target_dir)
    os.system(cmd)
    for item in bacteria_parser.data.isolate_list:
        if os.path.exists(item):
            os.system("cp {} {}/phytree_output/.".format(item, bacteria_parser.data.target_dir))
    header_name = bacteria_parser.data.reference_header_text.split()[0] + '.fsa'
    cmd = "~/bin/kma seq2fasta -t_db {} -seqs {} > {}/phytree_output/{}" \
        .format(bacteria_parser.data.bacteria_db, bacteria_parser.data.template_number, bacteria_parser.data.target_dir, header_name)
    os.system(cmd)

def ccphylo_tree(bacteria_parser):
    cmd = "~/bin/ccphylo tree --input {0}/phytree_output/distance_matrix --output {0}/phytree_output/tree.newick"\
        .format(bacteria_parser.data.target_dir)
    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0].decode()

# def create_phylo_tree(lpf_object):
#     with open ("{}phytree_output/tree.newick".format(bacteria_parser.data.target_dir)) as fd:
#         data = fd.read()
#     handle = StringIO(data)
#     tree = Phylo.read(handle, "newick")
#     matplotlib.rc('font', size=20)
#     fig = plt.figure(figsize=(20, 20), dpi=80)
#     axes = fig.add_subplot(1, 1, 1)
#     Phylo.draw(tree, axes=axes, do_show=False)
#     plt.savefig("{}/phytree_output/tree.png".format(bacteria_parser.data.target_dir), dpi=100)
#     bacteria_parser.data.phytree_path = "{}/phytree_output/tree.png".format(bacteria_parser.data.target_dir)
#     return lpf_object

# def plot_tree(treedata, output_file):
#     handle = StringIO(treedata)  # parse the newick string
#     tree = Phylo.read(handle, "newick")
#     matplotlib.rc('font', size=6)
#     # set the size of the figure
#     fig = plt.figure(figsize=(15, 15), dpi=100)
#     # alternatively
#     # fig.set_size_inches(10, 20)
#     axes = fig.add_subplot(1, 1, 1)
#     Phylo.draw(tree, axes=axes)
#     plt.savefig(output_file, dpi=100)
# 
#     return
