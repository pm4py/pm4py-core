import functools
from collections.abc import Mapping, Sequence


class Event(Mapping):

    def __init__(self, *args, **kw):
        self._dict = dict(*args, **kw)

    def __getitem__(self, key):
        return self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __str__(self):
        return str(self._dict)

    def project_on_attributes(self, keys):
        return Event({k: self[k] for k in keys})

    @staticmethod
    def project_on_attributes_static(event, keys):
        return Event({k: event[k] for k in keys})


class EventLog(Sequence):

    def __init__(self, *args):
        self._list = list(*args)

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

    def index(self, x, start: int = ..., end: int = ...):
        return self._list.index(x, start, end)

    def count(self, x):
        return self._list.count(x)

    def __str__(self):
        return str(self._list)

    def append(self, x):
        self._list.append(x)

    def project_events_on_attributes(self, keys):
        return EventLog(map(functools.partial(Event.project_on_attributes_static, keys=keys), self.events))

    def trace_view(self, key):
        trace_view = {}
        for event in self.events:
            if key in event.attributes:
                if event.attributes[key] in trace_view:
                    trace_view[event.attributes[key]].append(event)
                else:
                    trace_view[event.attributes[key]] = [event]
            else:
                raise KeyError('key %s not present in event %s' % (key, event))
        return trace_view