from pm4py.objects.ocel.obj import OCEL


class GPUOCEL(object):
    def __init__(self, ocel: OCEL):
        self._event_id_column = ocel.event_id_column
        self._object_id_column = ocel.object_id_column
        self._object_type_column = ocel.object_type_column
        self._event_activity = ocel.event_activity
        self._event_timestamp = ocel.event_timestamp
        self._qualifier = ocel.qualifier
        self._changed_field = ocel.changed_field
        self._events = ocel.events
        self._objects = ocel.objects
        self._relations = ocel.relations
        self._globals = ocel.globals
        self._o2o = ocel.o2o
        self._e2e = ocel.e2e
        self._object_changes = ocel.object_changes
        self._parameters = ocel.parameters

    @property
    def event_id_column(self):
        return self._event_id_column

    @property
    def object_id_column(self):
        return self._object_id_column

    @property
    def object_type_column(self):
        return self._object_type_column

    @property
    def event_activity(self):
        return self._event_activity

    @property
    def event_timestamp(self):
        return self._event_timestamp

    @property
    def qualifier(self):
        return self._qualifier

    @property
    def changed_field(self):
        return self._changed_field

    @property
    def events(self):
        return self._events

    @property
    def objects(self):
        return self._objects

    @property
    def relations(self):
        return self._relations

    @property
    def globals(self):
        return self._globals

    @property
    def o2o(self):
        return self._o2o

    @property
    def e2e(self):
        return self._e2e

    @property
    def object_changes(self):
        return self._object_changes

    @property
    def parameters(self):
        return self._parameters

    def to_ocel(self):
        ocel = OCEL(events=self._events, objects=self._objects, relations=self._relations, globals=self._globals, parameters=self._parameters, o2o=self._o2o, e2e=self._e2e, object_changes=self._object_changes)
        return ocel
