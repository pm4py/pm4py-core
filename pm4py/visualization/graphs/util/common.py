import os
import shutil
import subprocess
import sys
import tempfile


def get_temp_file_name(format):
    """
    Gets a temporary file name for the image

    Parameters
    ------------
    format
        Format of the target image
    """
    filename = tempfile.NamedTemporaryFile(suffix='.'+format)

    return filename.name


def save(temp_file_name, target_path):
    """
    Saves the temporary image associated to the graph to the specified path

    Parameters
    --------------
    temp_file_name
        Path to the temporary file hosting the graph
    target_path
        Path where the image shall eventually be saved
    """
    shutil.copyfile(temp_file_name, target_path)


def view(temp_file_name):
    """
    View the graph

    Parameters
    ------------
    temp_file_name
        Path to the temporary file hosting the graph
    """
    is_ipynb = False

    try:
        get_ipython()
        is_ipynb = True
    except NameError:
        pass

    if is_ipynb:
        from IPython.display import Image
        image = Image(open(temp_file_name, "rb").read())
        from IPython.display import display
        return display(image)
    else:
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', temp_file_name))
        elif os.name == 'nt':  # For Windows
            os.startfile(temp_file_name)
        elif os.name == 'posix':  # For Linux, Mac, etc.
            subprocess.call(('xdg-open', temp_file_name))
