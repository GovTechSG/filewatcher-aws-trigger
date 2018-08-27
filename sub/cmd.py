"""
Code implementation for running template command in external shell.
"""
import subprocess

from sub.base.invoker import Invoker

class CmdInvoker(Invoker):
    def __init__(self, cmd):
        self.cmd = cmd

    def invoke(self, path, event_type):
        """
        Helper function to trigger template command.
        Template command may contain:
        - {0} => path
        - {1} => event type number
        """
        interpolated_cmd = self.cmd.format(path, event_type)
        subprocess.run(interpolated_cmd, shell=True, check=True)
