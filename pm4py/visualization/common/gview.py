import tempfile

from pm4py.util import vis_utils, constants
from pm4py.visualization.common import dot_util
from io import BytesIO
from graphviz import Digraph


def view(gviz, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    format = str(gviz.format).lower()
    is_dot_installed = dot_util.check_dot_installed()

    if vis_utils.check_visualization_inside_jupyter():
        vis_utils.view_image_in_jupyter(gviz.render())
    else:
        return gviz.view(cleanup=True)


def matplotlib_view(gviz, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """
    format = str(gviz.format).lower()
    is_dot_installed = dot_util.check_dot_installed()

    from pm4py.visualization.common import save
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    file_name = tempfile.NamedTemporaryFile(suffix='.'+format)
    file_name.close()

    save.save(gviz, file_name.name)

    img = mpimg.imread(file_name.name)
    plt.imshow(img)
    plt.show()


def serialize_dot(gviz: Digraph, parameters=None) -> bytes:
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


def serialize(gviz: Digraph, parameters=None) -> bytes:
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
