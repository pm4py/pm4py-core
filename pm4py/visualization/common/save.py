import shutil
import os
from pm4py.visualization.common import dot_util, html


def save(gviz, output_file_path, parameters=None):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    format = os.path.splitext(output_file_path)[1][1:].lower()
    is_dot_installed = dot_util.check_dot_installed()

    if format.startswith("html"):
        html.save(gviz, output_file_path, parameters=parameters)
    else:
        render = gviz.render(cleanup=True)
        shutil.copyfile(render, output_file_path)
    """elif not is_dot_installed:
        raise Exception("impossible to save formats different from HTML without the Graphviz binary")"""

