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
        return hash(frozenset((str(x), str(y)) for x, y in self.items()))

    def __eq__(self, other):
        return frozenset((str(x), str(y)) for x, y in self.items()) == frozenset((str(x), str(y)) for x, y in other.items())

    def __copy__(self):
        event = Event()
        for k, v in self._dict.items():
            event[k] = v
        return event

    def __deepcopy__(self, memodict={}):
        event = Event()
        for k, v in self._dict.items():
            if type(v) is dict:
                event[k] = copy.deepcopy(v)
            else:
                event[k] = v
        return event


class EventStream(Sequence):

    def __init__(self, *args, **kwargs):
        self._attributes = kwargs['attributes'] if 'attributes' in kwargs else {}
        self._extensions = kwargs['extensions'] if 'extensions' in kwargs else {}
        self._omni = kwargs['omni_present'] if 'omni_present' in kwargs else kwargs[
            'globals'] if 'globals' in kwargs else {}
        self._classifiers = kwargs['classifiers'] if 'classifiers' in kwargs else {}
        self._properties = kwargs['properties'] if 'properties' in kwargs else {}
        self._list = list(*args)

    def __hash__(self):
        ret = 0
        for ev in self._list:
            ret += hash(ev)
            ret = ret % 479001599
        return ret

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        elif self.attributes != other.attributes:
            return False
        elif self.extensions != other.extensions:
            return False
        elif self.omni_present != other.omni_present:
            return False
        elif self.classifiers != other.classifiers:
            return False
        else:
            for i in range(len(self._list)):
                if self[i] != other[i]:
                    return False
        return True

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

    def _get_properties(self):
        return self._properties

    def _set_properties(self, properties):
        self._properties = properties

    def __copy__(self):
        event_stream = EventStream()
        event_stream._attributes = copy.copy(self._attributes)
        event_stream._extensions = copy.copy(self._extensions)
        event_stream._omni = copy.copy(self._omni)
        event_stream._classifiers = copy.copy(self._classifiers)
        event_stream._properties = copy.copy(self._properties)
        for ev in self._list:
            event_stream._list.append(ev)
        return event_stream

    def __deepcopy__(self, memodict={}):
        event_stream = EventStream()
        event_stream._attributes = copy.deepcopy(self._attributes)
        event_stream._extensions = copy.deepcopy(self._extensions)
        event_stream._omni = copy.deepcopy(self._omni)
        event_stream._classifiers = copy.deepcopy(self._classifiers)
        event_stream._properties = copy.deepcopy(self._properties)
        for ev in self._list:
            event_stream._list.append(copy.deepcopy(ev))
        return event_stream

    attributes = property(_get_attributes)
    extensions = property(_get_extensions)
    omni_present = property(_get_omni)
    classifiers = property(_get_classifiers)
    properties = property(_get_properties, _set_properties)


class Trace(Sequence):

    def __init__(self, *args, **kwargs):
        self._set_attributes(kwargs['attributes'] if 'attributes' in kwargs else {})
        self._properties = kwargs['properties'] if 'properties' in kwargs else {}
        self._list = list(*args)

    def __hash__(self):
        ret = 0
        for ev in self._list:
            ret += hash(ev)
            ret = ret % 479001599
        return ret

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        elif self.attributes != other.attributes:
            return False
        else:
            for i in range(len(self._list)):
                if self[i] != other[i]:
                    return False
        return True

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

    def _get_properties(self):
        return self._properties

    def _set_properties(self, properties):
        self._properties = properties

    attributes = property(_get_attributes)
    properties = property(_get_properties, _set_properties)

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
        new_attributes = {}
        for k, v in self.attributes.items():
            new_attributes[k] = v
        trace = Trace(attributes=new_attributes)
        for ev in self._list:
            trace.append(ev)
        return trace

    def __deepcopy__(self, memodict={}):
        new_attributes = {}
        for k, v in self.attributes.items():
            if type(new_attributes) is dict:
                new_attributes[k] = copy.deepcopy(v)
            else:
                new_attributes[k] = v
        trace = Trace(attributes=new_attributes)
        for ev in self._list:
            trace.append(copy.deepcopy(ev))
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
        log._properties = copy.copy(self._properties)
        for trace in self._list:
            log._list.append(trace)
        return log

    def __deepcopy__(self, memodict={}):
        log = EventLog()
        log._attributes = copy.deepcopy(self._attributes)
        log._extensions = copy.deepcopy(self._extensions)
        log._omni = copy.deepcopy(self._omni)
        log._classifiers = copy.deepcopy(self._classifiers)
        log._properties = copy.deepcopy(self._properties)
        for trace in self._list:
            log._list.append(copy.deepcopy(trace))
        return log

    def __hash__(self):
        ret = 0
        for trace in self._list:
            ret += hash(trace)
            ret = ret % 479001599
        return ret

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        elif self.attributes != other.attributes:
            return False
        elif self.extensions != other.extensions:
            return False
        elif self.omni_present != other.omni_present:
            return False
        elif self.classifiers != other.classifiers:
            return False
        else:
            for i in range(len(self._list)):
                if self[i] != other[i]:
                    return False
        return True
