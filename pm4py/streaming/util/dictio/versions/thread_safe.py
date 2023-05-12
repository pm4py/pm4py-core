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
from threading import Lock
from typing import Optional, Dict, Any, Union


class ThreadSafeDict(dict):
    def __init__(self, *args, **kw):
        super(ThreadSafeDict, self).__init__(*args, **kw)
        self.lock = Lock()
        self.itemlist = super(ThreadSafeDict, self).keys()

    def __setitem__(self, key, value):
        # TODO: what should happen to the order if
        #       the key is already in the dict
        self.lock.acquire()
        super(ThreadSafeDict, self).__setitem__(key, value)
        self.lock.release()

    def __iter__(self):
        self.lock.acquire()
        ret = iter(self.itemlist)
        self.lock.release()
        return ret

    def keys(self):
        self.lock.acquire()
        ret = set(self.itemlist)
        self.lock.release()
        return ret

    def values(self):
        self.lock.acquire()
        ret = [self[key] for key in self]
        self.lock.release()
        return ret

    def itervalues(self):
        self.lock.acquire()
        ret = (self[key] for key in self)
        self.lock.release()
        return ret


def apply(parameters: Optional[Dict[Any, Any]] = None):
    return ThreadSafeDict()
