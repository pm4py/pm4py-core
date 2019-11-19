import pyarrow

def apply(bytes, parameters=None):
    if parameters is None:
        parameters = {}


def import_from_file(file_path, parameters=None):
    if parameters is None:
        parameters = {}

    F = open(file_path, "rb")
    bytes = F.read()
    F.close()

    return apply(bytes, parameters=parameters)
