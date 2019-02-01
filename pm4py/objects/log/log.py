from collections.abc import Mapping, Sequence


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


class EventStream(Sequence):

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
