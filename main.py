import logging
import sys

from partner_tracker import setup_logging
from partner_tracker.driver import Driver
from partner_tracker.searchers import SearcherDancesportRu

setup_logging()
logger = logging.getLogger(__name__)


driver = Driver()

def start():
    searcher = SearcherDancesportRu()
    driver.add_searcher(searcher)
    driver.search()
    driver.update()
    driver.save()

def load():
    driver.load()

load()

