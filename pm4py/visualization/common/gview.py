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
import tempfile

from pm4py.util import vis_utils, constants
from io import BytesIO
from graphviz.dot import Digraph


def view(gviz):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    if vis_utils.check_visualization_inside_jupyter():
        vis_utils.view_image_in_jupyter(gviz.render())
    else:
        return gviz.view(cleanup=True)


def matplotlib_view(gviz):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    from pm4py.visualization.common import save
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    file_name = tempfile.NamedTemporaryFile(suffix='.png')
    file_name.close()

    save.save(gviz, file_name.name)

    img = mpimg.imread(file_name.name)
    plt.imshow(img)
    plt.show()


def serialize_dot(gviz: Digraph) -> bytes:
    """
    Serialize the DOT instructions of a Graphviz object

    Parameters
    --------------
    gviz
        Graphviz object

    Returns
    --------------
    bytes_string
        String containing the DOT instructions
    """
    dot = str(gviz)
    f = BytesIO()
    f.write(dot.encode(constants.DEFAULT_ENCODING))
    return f.getvalue()


def serialize(gviz: Digraph) -> bytes:
    """
    Serialize the image rendered from a Graphviz object

    Parameters
    ---------------
    gviz
        Graphviz object

    Returns
    ---------------
    bytes_string
        String containing the picture
    """
    render = gviz.render(cleanup=True)
    with open(render, "rb") as f1:
        return f1.read()
