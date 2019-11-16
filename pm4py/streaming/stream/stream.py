import collections
import threading
from concurrent.futures import ThreadPoolExecutor
from enum import Enum


class StreamState(Enum):
    INACTIVE = 1
    ACTIVE = 2
    FINISHED = 3


class LiveEventStream:

    def __init__(self):
        self._dq = collections.deque()
        self._state = StreamState.INACTIVE
        self._cond = threading.Condition(threading.Lock())
        self._observers = set()
        self._mail_man = None
        self._tp = ThreadPoolExecutor(6)

    def append(self, event):
        self._cond.acquire()
        if self._state != StreamState.FINISHED:
            self._dq.append(event)
            self._cond.notify()
        self._cond.release()

    def _deliver(self):
        while self._state != StreamState.INACTIVE:
            self._cond.acquire()
            while len(self._dq) == 0:
                if self._state != StreamState.FINISHED:
                    self._cond.wait()
                else:
                    return
            event = self._dq.popleft()
            for algo in self._observers:
                self._tp.submit(algo.receive, event)
            self._cond.release()

    def start(self):
        self._cond.acquire()
        self._state = StreamState.ACTIVE
        self._mail_man = threading.Thread(target=self._deliver)
        self._mail_man.start()
        self._cond.release()

    def stop(self):
        self._cond.acquire()
        if self._state == StreamState.ACTIVE:
            self._state = StreamState.FINISHED
        self._cond.release()

    def register(self, algo):
        self._cond.acquire()
        self._observers.add(algo)
        self._cond.release()

    async def deregister(self, algo):
        self._cond.acquire()
        self._observers.remove(algo)
        self._cond.release()

    def _get_state(self):
        return self._state

    state = property(_get_state)


