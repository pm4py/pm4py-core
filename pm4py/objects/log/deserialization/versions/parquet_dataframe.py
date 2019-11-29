import tempfile


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

    file = tempfile.NamedTemporaryFile(suffix=".dump")
    file.close()
    F = open(file.name, "wb")
    F.write(bytes)
    F.close()
    return import_from_file(file.name, parameters=parameters)


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

    from pm4py.objects.log.importer.parquet import factory as parquet_importer
    dataframe = parquet_importer.apply(file_path, parameters=parameters)

    return dataframe
