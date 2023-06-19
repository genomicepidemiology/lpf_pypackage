import logging
import os
import sys
import subprocess
from pathlib import Path

class prokkaRunner():
    def __init__(self, prefix, genome, entry_id, target_dir):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.prefix = prefix
        self.genome = genome
        self.entry_id = entry_id
        self.target_dir = target_dir

    def run(self):
        """runs kmergenetyper"""
        cmd = "docker run --name prokka_{} -v {}:/data/genome.fsa staphb/prokka prokka --outdir /output/prokka_output --centre virus_alignment --prefix prokka_results /data/genome.fsa"\
            .format(self.entry_id, self.genome)
        os.system(cmd)

        proc = subprocess.Popen("docker ps -aqf \"name={}_{}\"".format("prokka", self.entry_id),
                                shell=True,
                                stdout=subprocess.PIPE, )
        output = proc.communicate()[0]
        id = output.decode().rstrip()

        cmd = "docker cp {}:/output/prokka_output {}/prokka_output".format(id, self.target_dir)
        os.system(cmd)

        cmd = "docker container rm {}".format(id)
        os.system(cmd)