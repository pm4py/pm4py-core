import pyarrow


def apply(log, parameters=None):
    if parameters is None:
        parameters = {}


def export_to_file(log, file_path, parameters=None):
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
