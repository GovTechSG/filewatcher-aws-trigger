from abc import ABC, abstractmethod

class Invoker(ABC):
    @abstractmethod
    def invoke(self, path, event_type):
        pass
