import logging
from datetime import date
import warnings
import os


def setup_logger():
    warnings.filterwarnings('ignore')
    if not os.path.isdir('logs'):
        os.mkdir('logs')
    log_file = 'logs/app.{}.log'.format(date.today().isoformat())
    log_level = logging.INFO
    log_fmt = '[%(asctime)s] %(levelname)s (%(module)s-%(funcName)s-%(lineno)d) : %(message)s'
    logging.basicConfig(filename=log_file, level=log_level, format=log_fmt)
