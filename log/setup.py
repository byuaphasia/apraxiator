import logging
from datetime import datetime

def setup_logger():
    log_file = 'log/app.{}.log'.format(datetime.now().isoformat())
    log_level = logging.INFO
    log_fmt = '[%(asctime)s] %(levelname)s (%(module)s-%(funcName)s-%(lineno)d) : %(message)s'
    logging.basicConfig(filename=log_file, level=log_level, format=log_fmt)