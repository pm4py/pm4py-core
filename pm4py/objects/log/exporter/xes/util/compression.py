'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
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
