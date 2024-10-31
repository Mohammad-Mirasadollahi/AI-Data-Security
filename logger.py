import datetime
import logging
import os

from config import Config


def setup_logging():

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f'topic_modeling_{timestamp}.log'
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    log_path = os.path.join(Config.LOG_DIR, log_filename)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    return log_path
log_path = setup_logging()
logger = logging.getLogger(__name__)
