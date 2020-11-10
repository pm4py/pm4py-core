import abc
from threading import Lock
from typing import final


class StreamingAlgorithm(abc.ABC):
    def __init__(self, parameters=None):
        self._lock = Lock()

    @abc.abstractmethod
    def _process(self, event):
        pass

    @abc.abstractmethod
    def _current_result(self):
        pass

    @final
    def get(self):
        self._lock.acquire()
        ret = self._current_result()
        self._lock.release()
        return ret

    @final
    def receive(self, event):
        self._lock.acquire()
        self._process(event)
        self._lock.release()
