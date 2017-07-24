import logging
# Create a logger object.
import sys

import coloredlogs

logger = logging.getLogger(__name__)

coloredlogs.install(stream=sys.stdout, level='DEBUG', logger=logger)
