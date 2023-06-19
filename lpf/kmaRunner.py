import logging
import os
import sys
import subprocess
from pathlib import Path

class KMARunner():
    def __init__(self, input, output, reference_database, argument_string):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.check_for_kma()
        self.input = input
        self.output = output
        self.reference_database = reference_database
        self.argument_string = argument_string


    def check_for_kma(self):
        """Checks if kma is installed"""
        try:
            subprocess.call(["kma"], stdout=open(os.devnull, 'wb'))
        except FileNotFoundError:
            self.logger.info("kma is not installed in the local bin ~/bin/")
            sys.exit(1)

    def run(self):
        """runs kma"""
        kma_cmd = "kma -t_db {} -i {} -o {} {}".format(self.reference_database, self.input, self.output, self.argument_string)
        self.logger.info("Running KMA with the following command: {}".format(kma_cmd))
        self.logger.info(kma_cmd)
        os.system(kma_cmd)