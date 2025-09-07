import logging
from tqdm import tqdm

from pkg.api.constants import LUNII_LOGGER

class LuniiPacksLoggingHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
        except Exception:
            self.handleError(record)

def initialize_logger(logLVL):
    logger = logging.getLogger(LUNII_LOGGER)
    logger.addHandler(LuniiPacksLoggingHandler())
    logger.setLevel(logLVL)