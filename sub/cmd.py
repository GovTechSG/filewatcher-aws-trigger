"""
Code implementation for running template command in external shell.
"""
import subprocess

from sub.base.invoker import Invoker

#pylint: disable=too-few-public-methods
class CmdInvoker(Invoker):
    """
    Invoker for invoking template command with path and file event substituted.
    """
    def __init__(self, cmd):
        self.cmd = cmd

    def invoke(self, path, event_type):
        """
        Helper function to invoke and run template command.
        Template command may contain:
        - {0} => path
        - {1} => event type number
        """
        interpolated_cmd = self.cmd.format(path, event_type)
        subprocess.run(interpolated_cmd, shell=True, check=True)
