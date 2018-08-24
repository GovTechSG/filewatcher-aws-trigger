#!/usr/bin/env python3

"""
Filewatcher AWS trigger

This executable uses boto3, so the default AWS credentials can be set up based
it, e.g. ~/.aws/credentials and ~/.aws/config can be used.

Usage:
    app.py (-p <path> -n <name>) [-f <glob> -e <bitflag> --relative]
    app.py (-h | --help)

Options:
    -p <path>, --watchpath <path>       Path to watch recursively
    -n <name>, --name <name>            AWS Lambda function name to trigger
    -f <glob>, --filter <glob>          Glob pattern(s) for file matching (comma delimited) [default: *.*]
    -e <bitflag>, --event <bitflag>     Event type to trigger on (0=NONE, 1=CREATED, 2=DELETED, 4=MODIFIED, 8=MOVED) [default: 1]
    --relative                          Use relative path instead of absolute path for path matches
"""

from enum import Flag, auto
import logging
import json
import os
import sys
import time

import boto3
from docopt import docopt

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# logging falls under global
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('root')

class FileEvent(Flag):
    NONE = 0
    CREATED = auto()
    DELETED = auto()
    MODIFIED = auto()
    MOVED = auto()
    ALL = CREATED | DELETED | MODIFIED | MOVED


class Handler(PatternMatchingEventHandler):
    def __init__(self, file_event, lambda_name, use_abs_path, *args, **kwargs):
        super(Handler, self).__init__(*args, **kwargs)
        self.file_event = file_event
        self.lambda_name = lambda_name
        self.use_abs_path = use_abs_path

    def process(self, event):
        path = os.path.abspath(event.src_path) if self.use_abs_path else event.src_path
        logger.debug("{} - {}".format(path, event.event_type))

        trigger_lambda(
            self.lambda_name,
            json.dumps(dict(path=path)))

    def on_created(self, event):
        if self.file_event & FileEvent.CREATED:
            self.process(event)

    def on_deleted(self, event):
        if self.file_event & FileEvent.DELETED:
            self.process(event)

    def on_modified(self, event):
        if self.file_event & FileEvent.MODIFIED:
            self.process(event)

    def on_moved(self, event):
        if self.file_event & FileEvent.MOVED:
            self.process(event)


def trigger_lambda(name, payload):
    client = boto3.client('lambda')

    res = client.invoke(
        FunctionName=name,
        # InvocationType='Event',
        InvocationType='RequestResponse',
        Payload=payload
    )

    body = res['Payload'].read().decode('utf-8')
    logger.info(body)


def main():
    args = docopt(__doc__, version='FileWatcher AWS Trigger v0.1')
    logger.debug(args)

    watchpath = args['--watchpath']
    lambda_name = args['--name']
    glob_filters = args['--filter'].rstrip(',').split(',')
    event_bitflag = FileEvent(int(args['--event']))
    use_abs_path = not args['--relative']

    print('Filewatcher AWS Trigger program has started, CTRL-C to terminate...')

    event_handler = Handler(
        patterns=glob_filters,
        file_event=event_bitflag,
        use_abs_path=use_abs_path,
        ignore_directories=True,
        lambda_name=lambda_name)
    
    observer = Observer()
    observer.schedule(event_handler, watchpath, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == '__main__':
    main()
