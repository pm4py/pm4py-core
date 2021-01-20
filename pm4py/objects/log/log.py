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
import copy
from collections.abc import Mapping, Sequence
from enum import Enum


class XESExtension(Enum):
    ArtifactLifecycle = (
    'ArtifactLifecycle', 'artifactlifecycle', 'http://www.xes-standard.org/artifactlifecycle.xesext')
    Concept = ('Concept', 'concept', 'http://www.xes-standard.org/concept.xesext')
    Cost = ('Cost', 'cost', 'http://www.xes-standard.org/cost.xesext')
    Identity = ('Identity', 'identity', 'http://www.xes-standard.org/identity.xesext')
    Lifecycle = ('Lifecycle', 'lifecycle', 'http://www.xes-standard.org/lifecycle.xesext')
    Micro = ('Micro', 'micro', 'http://www.xes-standard.org/micro.xesext')
    Organizational = ('Organizational', 'org', 'http://www.xes-standard.org/org.xesext')
    Semantic = ('Semantic', 'semantic', 'http://www.xes-standard.org/semantic.xesext')
    SoftwareCommunication = ('Software Communication', 'swcomm', 'http://www.xes-standard.org/swcomm.xesext')
    SoftwareEvent = ('Software Event', 'swevent', 'http://www.xes-standard.org/swevent.xesext')
    SoftwareTelemetry = ('Software Telemetry', 'swtelemetry', 'http://www.xes-standard.org/swtelemetry.xesext')
    Time = ('Time', 'time', 'http://www.xes-standard.org/time.xesext')

    def __init__(self, name, prefix, uri):
        self._name = name
        self._prefix = prefix
        self._uri = uri

    @property
    def name(self):
        return self._name

    @property
    def prefix(self):
        return self._prefix

    @property
    def uri(self):
        return self._uri


class Event(Mapping):
    def __init__(self, *args, **kw):
        self._dict = dict(*args, **kw)

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __delitem__(self, key):
        del self._dict[key]

    def __repr__(self):
        return str(dict(self))

    def __hash__(self):
        return hash(frozenset(dict(self)))

    def __copy__(self):
        event = Event()
        event._dict = copy.copy(self._dict)
        return event


class EventStream(Sequence):

    def __init__(self, *args, **kwargs):
        self._attributes = kwargs['attributes'] if 'attributes' in kwargs else {}
        self._extensions = kwargs['extensions'] if 'extensions' in kwargs else {}
        self._omni = kwargs['omni_present'] if 'omni_present' in kwargs else kwargs[
            'globals'] if 'globals' in kwargs else {}
        self._classifiers = kwargs['classifiers'] if 'classifiers' in kwargs else {}
        self._list = list(*args)

    def __hash__(self):
        return hash(tuple(self))

    def __getitem__(self, key):
        return self._list[key]

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def __contains__(self, item):
        return item in self._list

    def __reversed__(self):
        return reversed(self._list)

    def __setitem__(self, key, value):
        self._list[key] = value

    def index(self, x, start: int = ..., end: int = ...):
        return self._list.index(x, start, end)

    def count(self, x):
        return self._list.count(x)

    def __str__(self):
        return str(self._list)

    def append(self, x):
        self._list.append(x)

    def _get_attributes(self):
        return self._attributes

    def _get_extensions(self):
        return self._extensions

    def _get_omni(self):
        return self._omni

    def _get_classifiers(self):
        return self._classifiers

    def __copy__(self):
        event_stream = EventStream()
        event_stream._attributes = copy.copy(self._attributes)
        event_stream._extensions = copy.copy(self._extensions)
        event_stream._omni = copy.copy(self._omni)
        event_stream._classifiers = copy.copy(self._classifiers)
        event_stream._list = copy.copy(self._list)
        return event_stream

    attributes = property(_get_attributes)
    extensions = property(_get_extensions)
    omni_present = property(_get_omni)
    classifiers = property(_get_classifiers)


class Trace(Sequence):

    def __init__(self, *args, **kwargs):
        self._set_attributes(kwargs['attributes'] if 'attributes' in kwargs else {})
        self._list = list(*args)

    def __hash__(self):
        tup = tuple(tuple(((x, y) for x, y in event.items())) for event in self._list)
        ret = hash(tup)
        return ret

    def __getitem__(self, key):
        return self._list[key]

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def __contains__(self, item):
        return item in self._list

    def __reversed__(self):
        return reversed(self._list)

    def __setitem__(self, key, value):
        self._list[key] = value

    def index(self, x, start: int = ..., end: int = ...):
        return self._list.index(x, start, end)

    def count(self, x):
        return self._list.count(x)

    def insert(self, i, x):
        self._list.insert(i, x)

    def append(self, x):
        self._list.append(x)

    def _set_attributes(self, attributes):
        self._attributes = attributes

    def _get_attributes(self):
        return self._attributes

    attributes = property(_get_attributes)

    def __repr__(self, ret_list=False):
        if len(self._list) == 0:
            ret = {"attributes": self._attributes, "events": []}
        elif len(self._list) == 1:
            ret = {"attributes": self._attributes, "events": [self._list[0]]}
        else:
            ret = {"attributes": self._attributes, "events": [self._list[0], "..", self._list[-1]]}
        if ret_list:
            return ret
        return str(ret)

    def __str__(self):
        return str(self.__repr__())

    def __copy__(self):
        trace = Trace()
        trace._attributes = copy.copy(self._attributes)
        trace._list = copy.copy(self._list)
        return trace


class EventLog(EventStream):
    def __init__(self, *args, **kwargs):
        super(EventLog, self).__init__(*args, **kwargs)

    def __repr__(self):
        if len(self._list) == 0:
            ret = []
        elif len(self._list) == 1:
            ret = [self._list[0].__repr__(ret_list=True)]
        else:
            ret = [self._list[0].__repr__(ret_list=True), "....", self._list[-1].__repr__(ret_list=True)]
        return str(ret)

    def __str__(self):
        return str(self.__repr__())

    def __copy__(self):
        log = EventLog()
        log._attributes = copy.copy(self._attributes)
        log._extensions = copy.copy(self._extensions)
        log._omni = copy.copy(self._omni)
        log._classifiers = copy.copy(self._classifiers)
        log._list = copy.copy(self._list)
        return log
