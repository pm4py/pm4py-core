import pyarrow
from pm4py.objects.log.log import EventLog, Trace, Event


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
    list_objs = pyarrow.deserialize(buffer)
    log = EventLog(attributes=list_objs[0], extensions=list_objs[1], omni_present=list_objs[2], classifiers=list_objs[3])
    for i in range(len(list_objs[4])):
        trace = Trace(attributes=list_objs[4][i])
        for j in range(len(list_objs[5][i])):
            trace.append(Event(list_objs[5][i][j]))
        log.append(trace)
    return log


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
