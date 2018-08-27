"""
Contains base class for Invoker for varying invocations.
"""
from abc import ABC, abstractmethod

#pylint: disable=too-few-public-methods
class Invoker(ABC):
    """
    Base class container standardized invocation method.
    """
    @abstractmethod
    def invoke(self, path, event_type):
        """
        Abstract method meant for deriving Invoker to override for invoking
        custom actions.
        """
        pass
