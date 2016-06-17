import logging
import sys
import pickle

from partner_tracker import setup_logging
from partner_tracker.driver import Driver
from partner_tracker.searchers import SearcherDancesportRu


setup_logging()
logger = logging.getLogger(__name__)


driver = Driver()
driver.load()


