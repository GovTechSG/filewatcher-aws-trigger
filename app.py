#!/usr/bin/env python3

"""
Filewatcher AWS trigger

Usage:
    app.py (-p <path>) [-f <glob>]
    app.py (-h | --help)

Options:
    -p <path>, --watchpath <path>     Path to watch recursively
    -f <glob>, --filter <glob>        Glob pattern(s) for file matching (comma delimited) [default: *.*]
"""

import logging
import os
import sys
import time

from docopt import docopt

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

if __name__ == '__main__':
    args = docopt(__doc__, version='FileWatcher AWS Trigger v0.1')
    print(args)

    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')

    # watchpath = sys.argv[1] if len(sys.argv) > 1 else '.'
    # event_handler = LoggingEventHandler()
    
    # observer = Observer()
    # observer.schedule(event_handler, watchpath, recursive=True)
    # observer.start()
    
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()

    # observer.join()
