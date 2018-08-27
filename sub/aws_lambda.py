"""
Code implementation for running AWS lambda function.
"""
import json

import boto3

from sub.base.invoker import Invoker

#pylint: disable=too-few-public-methods
class LambdaInvoker(Invoker):
    """
    Invoker for invoking AWS Lambda function.
    """
    def __init__(self, name):
        self.name = name

    def invoke(self, path, event_type):
        """
        Helper function to trigger and invoke the AWS lambda function based on
        the given name and payload. The payload should contain the JSON field
        'path' and 'event_type' in serialized byte format.
        """
        client = boto3.client('lambda')
        payload = json.dumps(dict(path=path, event_type=event_type))

        client.invoke(
            FunctionName=self.name,
            # InvocationType='Event',
            InvocationType='RequestResponse',
            Payload=payload
        )
