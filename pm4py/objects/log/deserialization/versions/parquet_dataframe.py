import tempfile

def apply(bytes, parameters=None):
    if parameters is None:
        parameters = {}

    file = tempfile.NamedTemporaryFile(suffix=".dump")
    file.close()
    F = open(file.name, "wb")
    F.write(bytes)
    F.close()
    return import_from_file(file.name, parameters=parameters)


def import_from_file(file_path, parameters=None):
    if parameters is None:
        parameters = {}

    from pm4py.objects.log.importer.parquet import factory as parquet_importer
    dataframe = parquet_importer.apply(file_path, parameters=parameters)

    return dataframe
