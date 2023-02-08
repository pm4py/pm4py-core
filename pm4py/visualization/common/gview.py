import tempfile

from pm4py.util import vis_utils, constants
from io import BytesIO
from graphviz import Digraph


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

def check_dot_installed():
    """
    Check if Graphviz's dot is installed correctly in the system

    Returns
    -------
    boolean
        Boolean telling if Graphviz's dot is installed correctly
    """
    import subprocess

    try:
        val = subprocess.run('dot -V', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return val.returncode == 0
    except:
        return False


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
