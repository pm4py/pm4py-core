import abc
from threading import Lock
#from typing import final
import traceback


class StreamingAlgorithm(abc.ABC):
    def __init__(self, parameters=None):
        self._lock = Lock()

    @abc.abstractmethod
    def _process(self, event):
        pass

    @abc.abstractmethod
    def _current_result(self):
        pass

    def get(self):
        self._lock.acquire()
        try:
            ret = self._current_result()
        except:
            traceback.print_exc()
            ret = None
        self._lock.release()
        return ret

    def receive(self, event):
        self._lock.acquire()
        try:
            self._process(event)
        except:
            traceback.print_exc()
        self._lock.release()
