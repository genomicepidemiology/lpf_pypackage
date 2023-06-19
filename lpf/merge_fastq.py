import os
import sys
import argparse


parser = argparse.ArgumentParser(description='.')
parser.add_argument('-version', action='version', version='lpf 1.1.0')
parser.add_argument("-folder", action="store", type=str, default = "", dest="folder", help="folder")
parser.add_argument("-name", action="store", type=str, default = "", dest="name", help="name")
args = parser.parse_args()

def merge():
    if args.name.endswith(".fastq.gz"):
        args.name = args.name[:-9]
    existing_list = os.listdir("/opt/lpf_data/")
    if args.name + ".fastq.gz" in existing_list:
        sys.exit('There is already a file with that name in the lpf_data folder. Please choose a different name.')
    cmd = 'cat {}*.fastq.gz > /opt/lpf_data/{}.fastq.gz'.format(args.folder, args.name)
    os.system(cmd)


def main():
    merge()

if __name__ == "__main__":
    merge()