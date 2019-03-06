import os
import shutil
import subprocess
import sys
import tempfile

import networkx as nx
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot


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


def apply(metric_values, parameters=None):
    """
    Perform SNA visualization starting from the Matrix Container object
    and the Resource-Resource matrix

    Parameters
    -------------
    metric_values
        Value of the metrics
    parameters
        Possible parameters of the algorithm, including:
            weight_threshold: the weight threshold to use in displaying the graph
            format: format of the output image (png, svg ...)

    Returns
    -------------
    temp_file_name
        Name of a temporary file where the visualization is placed
    """
    if parameters is None:
        parameters = {}

    weight_threshold = parameters["weight_threshold"] if "weight_threshold" in parameters else 0
    directed = metric_values[2]
    format = parameters["format"] if "format" in parameters else "png"

    temp_file_name = get_temp_file_name(format)

    rows, cols = np.where(metric_values[0] > weight_threshold)
    edges = zip(rows.tolist(), cols.tolist())

    if directed:
        graph = nx.DiGraph()
    else:
        graph = nx.Graph()

    labels = {}
    nodes = []
    for index, item in enumerate(metric_values[1]):
        labels[index] = item
        nodes.append(index)

    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    pyplot.clf()
    nx.draw(graph, with_labels=True, node_color=['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0'], labels=labels,
            node_size=500, pos=nx.circular_layout(graph))
    pyplot.savefig(temp_file_name, bbox_inches="tight")
    pyplot.clf()

    return temp_file_name


def view(temp_file_name, parameters=None):
    """
    View the SNA visualization on the screen

    Parameters
    -------------
    temp_file_name
        Temporary file name
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

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


def save(temp_file_name, dest_file, parameters=None):
    """
    Save the SNA visualization from a temporary file to a well-defined destination file

    Parameters
    -------------
    temp_file_name
        Temporary file name
    dest_file
        Destination file
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    shutil.copyfile(temp_file_name, dest_file)
