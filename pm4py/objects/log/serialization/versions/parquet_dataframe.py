import tempfile


def apply(log, parameters=None):
    if parameters is None:
        parameters = {}

    file_path = export_to_file(log, None, parameters=parameters)

    F = open(file_path, "rb")
    bytes = F.read()
    F.close()

    return bytes


def export_to_file(log, file_path, parameters=None):
    if parameters is None:
        parameters = {}

    if file_path is None:
        file_path = tempfile.NamedTemporaryFile(suffix=".parquet")
        file_path.close()
        file_path = file_path.name

    from pm4py.objects.log.exporter.parquet import factory as parquet_exporter
    parquet_exporter.apply(log, file_path, parameters=parameters)

    return file_path
