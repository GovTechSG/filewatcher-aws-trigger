#!/usr/bin/env python3

#pylint: disable=line-too-long
"""
Filewatcher AWS trigger

This executable uses boto3, so the default AWS credentials can be set up based
it, e.g. ~/.aws/credentials and ~/.aws/config can be used.

Usage:
    app.py (-p <path> -n <name>) [-f <glob> -e <bitflag> --force-poll --relative]
    app.py (-h | --help)

Options:
    -p <path>, --watchpath <path>       Path to watch recursively
    -n <name>, --name <name>            AWS Lambda function name to trigger
    -f <glob>, --filter <glob>          Glob pattern(s) for file matching (comma delimited) [default: *.*]
    -e <bitflag>, --event <bitflag>     Event type to trigger on (0=NONE, 1=CREATED, 2=DELETED, 4=MODIFIED, 8=MOVED) [default: 1]
    --force-poll                        Force using polling implementation, works for any platform [default: False]
    --relative                          Use relative path instead of absolute path for path matches
"""

from enum import Flag
import logging
import json
import os
import time

import boto3
from docopt import docopt

from watchdog.observers import Observer, polling
from watchdog.events import PatternMatchingEventHandler

# logging falls under global
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
LOGGER = logging.getLogger('root')

class FileEvent(Flag):
    """
    File event bit flag
    """
    NONE = 0
    CREATED = 1
    DELETED = 2
    MODIFIED = 4
    MOVED = 8
    ALL = CREATED | DELETED | MODIFIED | MOVED


class Handler(PatternMatchingEventHandler):
    """
    Implements PatternMatchingEventHandler with custom parameters to trigger
    AWS lambda function.
    """
    def __init__(self, file_event, lambda_name, use_abs_path, *args, **kwargs):
        super(Handler, self).__init__(*args, **kwargs)
        self.file_event = file_event
        self.lambda_name = lambda_name
        self.use_abs_path = use_abs_path

    def process(self, event):
        """
        Common processing function for all file event types.
        Triggers the AWS lambda function based on given name.
        Uses default AWS credentials.
        """
        path = os.path.abspath(event.src_path) if self.use_abs_path else event.src_path
        LOGGER.info("%s - %s", path, event.event_type)

        trigger_lambda(
            self.lambda_name,
            json.dumps(dict(path=path)))

    def on_created(self, event):
        """
        Processing function to trigger when file is being created.
        Only triggered when FileEvent.CREATED is passed into Handler.
        """
        if self.file_event & FileEvent.CREATED:
            self.process(event)

    def on_deleted(self, event):
        """
        Processing function to trigger when file is being created.
        Only triggered when FileEvent.DELETED is passed into Handler.
        """
        if self.file_event & FileEvent.DELETED:
            self.process(event)

    def on_modified(self, event):
        """
        Processing function to trigger when file is being created.
        Only triggered when FileEvent.MODIFIED is passed into Handler.
        """
        if self.file_event & FileEvent.MODIFIED:
            self.process(event)

    def on_moved(self, event):
        """
        Processing function to trigger when file is being created.
        Only triggered when FileEvent.MOVED is passed into Handler.
        """
        if self.file_event & FileEvent.MOVED:
            self.process(event)


def trigger_lambda(name, payload):
    """
    Helper function to triggers the AWS lambda function based on the given name
    and payload. The payload should contain the JSON field 'path' in serialized
    byte format.
    """
    client = boto3.client('lambda')

    res = client.invoke(
        FunctionName=name,
        # InvocationType='Event',
        InvocationType='RequestResponse',
        Payload=payload
    )

    body = res['Payload'].read().decode('utf-8')
    LOGGER.info(body)


def main():
    """
    Main function to call.
    """
    args = docopt(__doc__, version='FileWatcher AWS Trigger v0.1')
    LOGGER.debug(args)

    watchpath = args['--watchpath']
    lambda_name = args['--name']
    glob_filters = args['--filter'].rstrip(',').split(',')
    event_bitflag = FileEvent(int(args['--event']))
    force_poll = args['--force-poll']
    use_abs_path = not args['--relative']

    print('Filewatcher AWS Trigger program has started, CTRL-C to terminate...')

    event_handler = Handler(
        patterns=glob_filters,
        file_event=event_bitflag,
        use_abs_path=use_abs_path,
        ignore_directories=True,
        lambda_name=lambda_name)

    observer = Observer() if not force_poll else polling.PollingObserver()
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
