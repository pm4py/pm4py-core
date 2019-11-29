import pyarrow


def apply(log, parameters=None):
    """
    Serialize a log object to Pyarrow bytes

    Parameters
    --------------
    log
        Event log
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    serialization
        Serialized bytes
    """
    if parameters is None:
        parameters = {}

    list_objs = []
    list_objs.append(log.attributes)
    list_objs.append(log.extensions)
    list_objs.append(log.omni_present)
    list_objs.append(log.classifiers)
    list_objs.append([trace.attributes for trace in log])
    list_objs.append([[dict(y) for y in trace._list] for trace in log])

    return pyarrow.serialize(list_objs).to_buffer().to_pybytes()


def export_to_file(log, file_path, parameters=None):
    """
    Serialize a log object to the content of a file

    Parameters
    --------------
    log
        Event log
    file_path
        File path (if None, then a temp file is targeted)
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    file_path
        File path
    """
    if parameters is None:
        parameters = {}

    if file_path is None:
        import tempfile
        file_path = tempfile.NamedTemporaryFile(suffix=".dump")
        file_path.close()
        file_path = file_path.name

    F = open(file_path, "wb")
    F.write(apply(log, parameters=parameters))
    F.close()

    return file_path
