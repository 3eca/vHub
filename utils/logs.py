import os

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Create Logger
    :param name: Logger name
    :param path_log: path to log file
    :return: Logger
    """
    log_directory = './logs'
    log_file = '/vhub.log'
    log_full_path = ''.join((log_directory, log_file))

    if not os.path.exists(log_directory):
        os.mkdir(log_directory)
    if not os.path.exists(log_full_path):
        os.mknod(log_full_path)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_full_path, mode='a', encoding='utf-8')
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        logging.Formatter('[%(name)s - %(asctime)s - %(levelname)s]: %(message)s'))
    logger.addHandler(handler)
    return logger


if __name__ == '__main__':
    pass
