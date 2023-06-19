import hashlib
import json

def md5_of_sequence(sequence):
    hash_md5 = hashlib.md5(sequence.encode())
    return hash_md5.hexdigest()

def md5_of_file(file_path):
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        lines = f.read()
        m.update(lines)
    md5code = m.hexdigest()
    return md5code

def md5_from_input_json(input_json):
    with open(input_json, 'r') as f:
        data = json.load(f)
    return md5_of_file(data['input_path'])