import os
import sys

def derive_file_list_from_template_header_text(template_):
def make_ccphylo_folder(file_list, output_path):
    cmd = "mkdir {}/phytree_output".format(output_path)
    os.system(cmd)

    for item in file_list:
        if os.path.exists(item):
            os.system("cp {} {}/phytree_output/.".format(item, output_path))

def create_phylo_tree(lpf_object):
    with open ("{}phytree_output/tree.newick".format(lpf_object.target_dir)) as fd:
        data = fd.read()
    handle = StringIO(data)
    tree = Phylo.read(handle, "newick")
    matplotlib.rc('font', size=20)
    fig = plt.figure(figsize=(20, 20), dpi=80)
    axes = fig.add_subplot(1, 1, 1)
    Phylo.draw(tree, axes=axes, do_show=False)
    plt.savefig("{}/phytree_output/tree.png".format(lpf_object.target_dir), dpi=100)
    lpf_object.phytree_path = "{}/phytree_output/tree.png".format(lpf_object.target_dir)
    return lpf_object

def plot_tree(treedata, output_file):
    handle = StringIO(treedata)  # parse the newick string
    tree = Phylo.read(handle, "newick")
    matplotlib.rc('font', size=6)
    # set the size of the figure
    fig = plt.figure(figsize=(15, 15), dpi=100)
    # alternatively
    # fig.set_size_inches(10, 20)
    axes = fig.add_subplot(1, 1, 1)
    Phylo.draw(tree, axes=axes)
    plt.savefig(output_file, dpi=100)

    return
