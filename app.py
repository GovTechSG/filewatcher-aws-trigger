#!/usr/bin/env python3

#pylint: disable=line-too-long
"""
Filewatch Trigger

Triggers possibly the following actions based on provided parameters:
- AWS Lambda function
- Shell template command (with path and file event type)

For AWS, this application uses boto3, so the default AWS credentials can be set
up based on boto3, e.g. ~/.aws/credentials and ~/.aws/config can be used.

Usage:
    app.py aws-lambda (-p <path> -n <name>) [-f <glob> -e <bitflag> --force-poll --relative]
    app.py cmd (-p <path> -c <cmd>) [-f <glob> -e <bitflag> --force-poll --relative]
    app.py (-h | --help)

Options:
    -p <path>, --watchpath <path>       Path to watch recursively
    -c <cmd>, --cmd <cmd>               Command to run when there is a file trigger
    -n <name>, --name <name>            AWS Lambda function name to trigger
    -f <glob>, --filter <glob>          Glob pattern(s) for file matching (comma delimited) [default: *.*]
    -e <bitflag>, --event <bitflag>     Event type to trigger on (0=NONE, 1=CREATED, 2=DELETED, 4=MODIFIED, 8=MOVED) [default: 1]
    --force-poll                        Force using polling implementation, works for any platform
    --relative                          Use relative path instead of absolute path for path matches
"""

from enum import Flag
import logging
import os
import time

from docopt import docopt
from watchdog.observers import Observer, polling
from watchdog.events import PatternMatchingEventHandler

from sub.aws_lambda import LambdaInvoker
from sub.cmd import CmdInvoker

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
    the given invoker.
    """
    def __init__(self, invoker, file_event, use_abs_path, *args, **kwargs):
        super(Handler, self).__init__(*args, **kwargs)
        self.invoker = invoker
        self.file_event = file_event
        self.use_abs_path = use_abs_path

    def process(self, event):
        """
        Common processing function for all file event types.
        Triggers the AWS lambda function based on given name.
        Uses default AWS credentials.
        """
        path = os.path.abspath(event.src_path) if self.use_abs_path else event.src_path
        event_type = event.event_type
        LOGGER.info("%s - %s", path, event.event_type)

        self.invoker.invoke(path, event_type)


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


def main():
    """
    Main function to call.
    """
    args = docopt(__doc__, version='Filewatch Trigger v0.2.0')
    LOGGER.debug(args)

    is_aws_lambda_type = args['aws-lambda']
    is_cmd_type = args['cmd']

    # common options
    watchpath = args['--watchpath']
    glob_filters = args['--filter'].rstrip(',').split(',')
    event_bitflag = FileEvent(int(args['--event']))
    force_poll = args['--force-poll']
    use_abs_path = not args['--relative']

    # aws-lambda only
    lambda_name = args['--name'] if is_aws_lambda_type else None

    # cmd only
    cmd = args['--cmd'] if is_cmd_type else None

    def select_invoker():
        if is_aws_lambda_type:
            return LambdaInvoker(lambda_name)
        if is_cmd_type:
            return CmdInvoker(cmd)
        raise Exception("Invalid subcommand used")

    invoker = select_invoker()
    print('Filewatch Trigger program has started, CTRL-C to terminate...')

    event_handler = Handler(
        patterns=glob_filters,
        invoker=invoker,
        file_event=event_bitflag,
        use_abs_path=use_abs_path,
        ignore_directories=True)

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
