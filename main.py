import logging
import argparse
import sys

from partner_tracker import setup_logging
from partner_tracker.driver import Driver
from partner_tracker.searchers import SearcherDancesportRu

setup_logging()
logger = logging.getLogger(__name__)


VERSION = 0.01
STORAGE_FILENAME = 'data.p'


def main():
    parser = argparse.ArgumentParser(description='Interactive cli application for keeping notes about partners')
    subparsers = parser.add_subparsers()

    parser_load = subparsers.add_parser('load', help='Load data from disk, overwrites current state')
    parser_load.add_argument('filename', type=str, default=STORAGE_FILENAME, help='Set source filename. Default is %s' % STORAGE_FILENAME)

    parser_save = subparsers.add_parser('save', help='Save data to disk')
    parser_save.add_argument('filename', type=str, default=STORAGE_FILENAME, help='Set destination filename. Default is %s' % STORAGE_FILENAME)

    parser_list = subparsers.add_parser('list', help='Print list of partners to console')
    parser_list.add_argument('--state', '-s', help='Filter by state')

    parser_open = subparsers.add_parser('open', help='Open list of partners in default web browser')
    parser_open.add_argument('--state', '-s', help='Filter by state')

    parser_quit = subparsers.add_parser('quit', help='Close program')


    while True:
        args = input('Enger command: ')
        try:
            args = parser.parse_args(args_string.split())
        except SystemExit:
            pass



driver = Driver()

def start():
    searcher = SearcherDancesportRu()
    driver.add_searcher(searcher)
    driver.search()
    driver.update()
    driver.save()

def load():
    driver.load()





