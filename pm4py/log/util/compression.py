import tempfile, gzip, shutil

def decompress(gzipped_xes):
    """
    Decompress a gzipped XES and returns location of the temp file created

    Parameters
    ----------
    gzipped_xes
        Gzipped XES

    Returns
    ----------
    decompressedPath
        Decompressed file path
    """
    fp = tempfile.NamedTemporaryFile(suffix='.xes')
    fp.close()
    with gzip.open(gzipped_xes, 'rb') as f_in:
        with open(fp.name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return fp.name