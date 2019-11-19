import pyarrow
from pm4py.objects.log.log import Event, EventStream


def apply(bytes, parameters=None):
    if parameters is None:
        parameters = {}
    buffer = pyarrow.py_buffer(bytes)
    list_events = pyarrow.deserialize(buffer)
    for i in range(len(list_events)):
        list_events[i] = Event(list_events[i])
    return EventStream(list_events)

def import_from_file(file_path, parameters=None):
    if parameters is None:
        parameters = {}
