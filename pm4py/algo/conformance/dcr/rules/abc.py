from abc import ABC, abstractmethod

class CheckFrame(ABC):
    """
    the CheckFrame Class creates an interface, that specifies which functionality that associated class should have
    """
    @abstractmethod
    def check_rule(self, *args, **kwargs):
        pass