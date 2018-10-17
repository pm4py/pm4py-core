import tempfile


def import_string_to_temp_file(stri, extension):
    """
    Import string to temporary file

    Parameters
    -----------
    stri
        String
    extension
        Temporary file extension

    Returns
    -----------
    path
        Temporary file path
    """
    fp = tempfile.NamedTemporaryFile(suffix='.' + extension)
    fp.close()
    with open(fp.name, 'w') as f:
        f.write(stri)
    return fp.name
