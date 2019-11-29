import tempfile


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

    file_path = export_to_file(log, None, parameters=parameters)

    F = open(file_path, "rb")
    bytes = F.read()
    F.close()

    return bytes


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
        file_path = tempfile.NamedTemporaryFile(suffix=".parquet")
        file_path.close()
        file_path = file_path.name

    from pm4py.objects.log.exporter.parquet import factory as parquet_exporter
    parquet_exporter.apply(log, file_path, parameters=parameters)

    return file_path
