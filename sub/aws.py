"""
Code implementation for running AWS lambda function.
"""
import json
import os

import boto3

from sub.base.invoker import Invoker

class LambdaInvoker(Invoker):
    def __init__(self, name):
        self.name = name

    def invoke(self, path, event_type):
        """
        Helper function to triggers the AWS lambda function based on the given
        name and payload. The payload should contain the JSON field 'path' in
        serialized byte format.
        """
        client = boto3.client('lambda')
        payload = json.dumps(dict(path=path, event_type=event_type))

        client.invoke(
            FunctionName=self.name,
            # InvocationType='Event',
            InvocationType='RequestResponse',
            Payload=payload
        )
