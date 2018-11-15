import random
from collections.abc import Mapping, Sequence
from copy import copy


class Event(Mapping):
    """ Object useful for the second
    maximal cut detection algorithm """

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


class EventLog(Sequence):

    def __init__(self, *args, **kwargs):
        self._attributes = kwargs['attributes'] if 'attributes' in kwargs else {}
        self._extensions = kwargs['extensions'] if 'extensions' in kwargs else {}
        self._omni = kwargs['omni_present'] if 'omni_present' in kwargs else kwargs[
            'globals'] if 'globals' in kwargs else {}
        self._classifiers = kwargs['classifiers'] if 'classifiers' in kwargs else {}
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

    def sort(self, timestamp_key="time:timestamp", reverse_sort=False):
        """
        Sort an event log based on timestamp key

        Parameters
        -----------
        timestamp_key
            Timestamp key
        reverse_sort
            If true, reverses the direction in which the sort is done (ascending)
        """
        self._list.sort(key=lambda x: x[timestamp_key], reverse=reverse_sort)

    def sample(self, no_events=100):
        """
        Randomly sample a fixed number of events from the original log

        Parameters
        -----------
        no_events
            Number of events that the sample should have

        Returns
        -----------
        newLog
            Filtered log
        """
        new_log = EventLog(attributes=self.attributes, extensions=self.extensions, globals=self._omni,
                           classifiers=self.classifiers)
        set_events = set()
        for i in range(0, min(no_events, len(self._list))):
            set_events.add(random.randrange(0, len(self._list)))
        set_events = list(set_events)
        set_events.sort()
        for event in set_events:
            new_log.append(copy(self._list[event]))
        return new_log

    def insert_event_index_as_event_attribute(self, event_index_attr_name="@@eventindex"):
        """
        Insert the current event index as event attribute

        Parameters
        -----------
        event_index_attr_name
            Attribute name given to the event index
        """

        if not type(self) is TraceLog:
            for i in range(0, len(self._list)):
                self._list[i][event_index_attr_name] = i + 1

    attributes = property(_get_attributes)
    extensions = property(_get_extensions)
    omni_present = property(_get_omni)
    classifiers = property(_get_classifiers)


class Trace(Sequence):

    def __init__(self, *args, **kwargs):
        self._set_attributes(kwargs['attributes'] if 'attributes' in kwargs else {})
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

    def sort(self, timestamp_key="time:timestamp", reverse_sort=False):
        """
        Sort a trace based on timestamp key

        Parameters
        -----------
        timestamp_key
            Timestamp key
        reverse_sort
            If true, reverses the direction in which the sort is done (ascending)
        """
        self._list.sort(key=lambda x: x[timestamp_key], reverse=reverse_sort)

    attributes = property(_get_attributes)

    def __repr__(self):
        return str({"attributes": self._attributes, "events": self._list})


class TraceLog(EventLog):
    def __init__(self, *args, **kwargs):
        super(TraceLog, self).__init__(*args, **kwargs)

    def sort(self, timestamp_key="time:timestamp", reverse_sort=False):
        """
        Sort a trace log based on timestamp key

        Parameters
        -----------
        timestamp_key
            Timestamp key
        reverse_sort
            If true, reverses the direction in which the sort is done (ascending)
        """
        self._list = [x for x in self._list if len(x) > 0]
        for trace in self._list:
            trace.sort(timestamp_key=timestamp_key, reverse_sort=reverse_sort)
        self._list.sort(key=lambda x: x[0][timestamp_key], reverse=reverse_sort)

    def sample(self, no_traces=100):
        """
        Randomly sample a fixed number of traces from the original log

        Parameters
        -----------
        no_traces
            Number of traces that the sample should have

        Returns
        -----------
        newLog
            Filtered log
        """
        new_log = TraceLog(attributes=self.attributes, extensions=self.extensions, globals=self._omni,
                           classifiers=self.classifiers)
        set_traces = set()
        for i in range(0, min(no_traces, len(self._list))):
            set_traces.add(random.randrange(0, len(self._list)))
        set_traces = list(set_traces)
        set_traces.sort()
        for trace in set_traces:
            new_log.append(copy(self._list[trace]))
        return new_log

    def insert_trace_index_as_event_attribute(self, trace_index_attr_name="@@traceindex"):
        """
        Inserts the current trace index as event attribute
        (overrides previous values if needed)

        Parameters
        -----------
        trace_index_attr_name
            Attribute name given to the trace index
        """
        for i in range(len(self._list)):
            for j in range(len(self._list[i])):
                self._list[i][j][trace_index_attr_name] = i + 1
