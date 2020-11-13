import shutil

from pm4py.util.vis_utils import human_readable_stat, get_arc_penwidth, get_trans_freq_color, get_base64_from_gviz, \
    get_base64_from_file
from pm4py.util import vis_utils


def save(gviz, output_file_path):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    render = gviz.render(cleanup=True)
    shutil.copyfile(render, output_file_path)


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
