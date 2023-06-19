import logging
import os
import sys
import subprocess
from pathlib import Path

class kmergenetyperRunner():
    def __init__(self, nanopore, database, md, output):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.nanopore = nanopore
        self.database = database
        self.md = md
        self.output = output


    def run(self):
        """runs kmergenetyper"""
        kmergenetyper_cmd = "kmergenetyper -nanopore {} -t_db {} -o {} -md {}".format(self.nanopore, self.database, self.output, self.md)
        self.logger.info("Running kmergenetyper with the following command: {}".format(kmergenetyper_cmd))
        os.system(kmergenetyper_cmd)