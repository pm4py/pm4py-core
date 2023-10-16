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
import shutil
import tempfile

from pm4py.util import vis_utils, constants


def get_temp_file_name(format):
    """
    Gets a temporary file name for the image

    Parameters
    ------------
    format
        Format of the target image
    """
    filename = tempfile.NamedTemporaryFile(suffix='.' + format)

    name = filename.name

    filename.close()

    return name


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
    if constants.DEFAULT_GVIZ_VIEW == "matplotlib_view":
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        img = mpimg.imread(temp_file_name)
        plt.axis('off')
        plt.tight_layout(pad=0, w_pad=0, h_pad=0)
        plt.imshow(img)
        plt.show()
        return
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


def serialize(temp_file_name: str) -> bytes:
    """
    Serializes the graph

    Parameters
    ------------
    temp_file_name
        Path to the temporary file hosting the graph
    """
    with open(temp_file_name, "rb") as f:
        return f.read()
