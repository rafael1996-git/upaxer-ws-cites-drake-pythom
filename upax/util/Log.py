import logging


def message(string):
    if False:
        print(str(string))
    else:
        logging.warning(str(string))
