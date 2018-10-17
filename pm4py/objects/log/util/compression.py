import gzip
import os
import shutil
import tempfile


def compress(file):
    """
    Compress a file in-place adding .gz suffix

    Parameters
    -----------
    file
        Uncompressed file

    Returns
    -----------
    compressed_file
        Compressed file path
    """
    extension = file.split(".")[-1] + ".gz"
    fp = tempfile.NamedTemporaryFile(suffix=extension)
    fp.close()
    with open(file, 'rb') as f_in:
        with gzip.open(fp.name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    shutil.move(fp.name, file + ".gz")
    os.remove(file)
    return file


def decompress(gzipped_file):
    """
    Decompress a gzipped file and returns location of the temp file created

    Parameters
    ----------
    gzipped_file
        Gzipped file

    Returns
    ----------
    decompressedPath
        Decompressed file path
    """
    extension = gzipped_file.split(".")[-1]
    fp = tempfile.NamedTemporaryFile(suffix=extension)
    fp.close()
    with gzip.open(gzipped_file, 'rb') as f_in:
        with open(fp.name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return fp.name
