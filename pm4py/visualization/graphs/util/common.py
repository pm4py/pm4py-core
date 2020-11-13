import shutil
import tempfile

from pm4py.util import vis_utils


def get_temp_file_name(format):
    """
    Gets a temporary file name for the image

    Parameters
    ------------
    format
        Format of the target image
    """
    filename = tempfile.NamedTemporaryFile(suffix='.' + format)

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
    if vis_utils.check_visualization_inside_jupyter():
        vis_utils.view_image_in_jupyter(temp_file_name)
    else:
        vis_utils.open_opsystem_image_viewer(temp_file_name)


def matplotlib_view(temp_file_name):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    temp_file_name
        Path to the temporary file hosting the graph
    """
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    img = mpimg.imread(temp_file_name)
    plt.imshow(img)
    plt.show()
