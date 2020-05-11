import gzip
import os
import shutil
import tempfile


# this is ugly, should be done internally in the exporter...
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
