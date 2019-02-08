import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from pyvis.network import Network


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

    Returns
    -------------
    temp_file_name
        Name of a temporary file where the visualization is placed
    """
    if parameters is None:
        parameters = {}

    weight_threshold = parameters["weight_threshold"] if "weight_threshold" in parameters else 0
    directed = metric_values[2]

    temp_file_name = get_temp_file_name("html")

    rows, cols = np.where(metric_values[0] > weight_threshold)
    weights = list()

    for x in range(len(rows)):
        weights.append(metric_values[0][rows[x]][cols[x]])

    got_net = Network(height="750px", width="100%", bgcolor="black", font_color="#3de975", directed=directed)
    # set the physics layout of the network
    got_net.barnes_hut()

    edge_data = zip(rows, cols, weights)

    for e in edge_data:
        src = metric_values[1][e[0]]  # convert ids to labels
        dst = metric_values[1][e[1]]
        w = e[2]

        # I have to add some options here, there is no parameter
        highlight = {'border': "#3de975", 'background': "#41e9df"}
        # color = {'border': "#000000", 'background': "#123456"}
        got_net.add_node(src, src, title=src, labelHighlightBold=True, color={'highlight': highlight})
        got_net.add_node(dst, dst, title=dst, labelHighlightBold=True, color={'highlight': highlight})
        got_net.add_edge(src, dst, value=w, title=w)

    neighbor_map = got_net.get_adj_list()

    dict = got_net.get_edges()

    # add neighbor data to node hover data
    for node in got_net.nodes:
        counter = 0
        if directed:
            node["title"] = "<h3>" + node["title"] + " Output Links: </h3>"
        else:
            node["title"] = "<h3>" + node["title"] + " Links: </h3>"
        for neighbor in neighbor_map[node["id"]]:
            if (counter % 10 == 0):
                node["title"] += "<br>::: " + neighbor
            else:
                node["title"] += " ::: " + neighbor
            node["value"] = len(neighbor_map[node["id"]])
            counter += 1

    got_net.show_buttons(filter_=['nodes', 'edges', 'physics'])

    got_net.write_html(temp_file_name)

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
        raise Exception("pyvis visualization not working inside Jupyter notebooks")
        from IPython.display import IFrame
        return IFrame(temp_file_name, width="100%", height="750px")
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
