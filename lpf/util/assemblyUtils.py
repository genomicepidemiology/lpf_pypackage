import os
import subprocess

def run_bandage(bacteria_parser):
    #TBD run bandage in assembly func
    cmd = "docker run --name bandage{} -v {}/assembly_results/:/data/assembly_results/ nanozoo/bandage Bandage image /data/assembly_results/assembly_graph.gfa contigs.jpg".format(
        bacteria_parser.data.entry_id, bacteria_parser.data.target_dir)
    os.system(cmd)

    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("bandage", bacteria_parser.data.entry_id), shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:contigs.jpg {}/contigs.jpg".format(id, bacteria_parser.data.target_dir)
    os.system(cmd)

    cmd = "docker container rm {}".format(id)
    os.system(cmd)


def run_quast(bacteria_parser):
    cmd = "docker run --name quast{} -v {}/assembly_results/:/data/assembly_results/ staphb/quast quast.py /data/assembly_results/assembly.fasta -o /output/quast_output".format(
        bacteria_parser.data.entry_id, bacteria_parser.data.target_dir)
    os.system(cmd)

    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("quast", bacteria_parser.data.entry_id), shell=True,
                            stdout=subprocess.PIPE, )
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:/output/quast_output {}/quast_output".format(id, bacteria_parser.data.target_dir)
    os.system(cmd)

    cmd = "docker container rm {}".format(id)
    os.system(cmd)


def flye_assembly(bacteria_parser):
    cmd = "docker run --name assembly_{0} -v {1}:/tmp/{2} staphb/flye flye -o /tmp/assembly_results" \
          " --threads 8 --nano-raw /tmp/{2}"\
        .format(bacteria_parser.data.entry_id, bacteria_parser.data.input_path, bacteria_parser.data.input_file)
    print (cmd)
    os.system(cmd)

    proc = subprocess.Popen("docker ps -aqf \"name={}{}\"".format("assembly_", bacteria_parser.data.entry_id), shell=True, stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    id = output.decode().rstrip()

    cmd = "docker cp {}:/tmp/assembly_results {}/assembly_results".format(id, bacteria_parser.data.target_dir)
    os.system(cmd)
    cmd = "docker container rm {}".format(id)
    os.system(cmd)

    # Concatenate contigs
    with open("{}/assembly_results/assembly.fasta".format(bacteria_parser.data.target_dir), 'r') as infile:
        with open("{}/{}_assembly.fasta".format(bacteria_parser.data.target_dir, bacteria_parser.data.sample_name), 'w') as outfile:
            sequence = ""
            for line in infile:
                if line[0] != ">":
                    line = line.rstrip()
                    sequence += line

            if bacteria_parser.data.reference_header_text.startswith(">Assembly"):
                new_header_text = ">{}\tAssembly\t{}".format(bacteria_parser.data.entry_id, bacteria_parser.data.reference_header_text[1:]
                                                           .split("\tAssembly\t")[-1])
            else:
                new_header_text = ">{}\tAssembly\t{}".format(bacteria_parser.data.entry_id, bacteria_parser.data.reference_header_text[1:])
            print(new_header_text, file=outfile)
            print(sequence, file=outfile)

    #Move indexing to after check in assembly was completed correctly
    test_list = ['62b06be200d3967db6b0f6023d7b5b2e', 'fac82762aa980d285edbbcd45ce952fb'] #IDs of test files to be ignored
    if bacteria_parser.data.entry_id not in test_list:
        os.system("~/bin/kma index -t_db {} -i {}{}_assembly.fasta"\
                  .format(bacteria_parser.data.bacteria_db, bacteria_parser.data.target_dir, bacteria_parser.data.sample_name))