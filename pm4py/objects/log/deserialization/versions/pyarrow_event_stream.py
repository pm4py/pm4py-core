import pyarrow
from pm4py.objects.log.log import Event, EventStream


def apply(bytes, parameters=None):
    """
    Apply the deserialization to the bytes produced by Pyarrow serialization

    Parameters
    --------------
    bytes
        Bytes
    parameters
        Parameters of the algorithm

    Returns
    --------------
    deser
        Deserialized object
    """
    if parameters is None:
        parameters = {}
    buffer = pyarrow.py_buffer(bytes)
    list_events = pyarrow.deserialize(buffer)
    for i in range(len(list_events)):
        list_events[i] = Event(list_events[i])
    return EventStream(list_events)


def import_from_file(file_path, parameters=None):
    """
    Apply the deserialization to a file produced by Pyarrow serialization

    Parameters
    --------------
    file_path
        File path
    parameters
        Parameters of the algorithm

    Returns
    --------------
    deser
        Deserialized object
    """
    if parameters is None:
        parameters = {}

    F = open(file_path, "rb")
    bytes = F.read()
    F.close()

    return apply(bytes, parameters=parameters)
