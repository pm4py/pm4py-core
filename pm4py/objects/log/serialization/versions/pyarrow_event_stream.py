import pyarrow


def preprocess_stream(stream):
    stream = list(stream)
    for i in range(len(stream)):
        stream[i] = dict(stream[i])
    return stream


def apply(log, parameters=None):
    if parameters is None:
        parameters = {}
    log = preprocess_stream(log)
    return pyarrow.serialize(log).to_buffer().to_pybytes()


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

