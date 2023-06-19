import os
import sys
import logging

def move_list_of_files(file_list, output_dir):
    """Moves a list of files to the output directory"""
    create_output_dir(output_dir)
    for file in file_list:
        os.system("mv {} {}".format(file, output_dir))

def create_output_dir(output_dir):
    """Creates the output directory if it does not exist"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
