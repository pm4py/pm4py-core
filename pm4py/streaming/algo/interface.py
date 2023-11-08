'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import abc
from threading import Lock
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
