import abc
from abc import ABC


class StreamingAlgorithm(abc.ABC):

    @abc.abstractmethod
    def receive(self, event):
        pass
