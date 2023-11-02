from abc import ABC, abstractmethod

class CheckFrame(ABC):
    @abstractmethod
    def check_rule(cls, *args, **kwargs):
        pass