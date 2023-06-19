import logging

def begin_logging(file):
    try:
        logging.basicConfig(
            format='%(asctime)s %(message)s',
            filename=file,
            level=logging.INFO)
    except PermissionError:
        pass