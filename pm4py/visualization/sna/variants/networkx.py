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
from copy import copy
from enum import Enum

import matplotlib
import numpy as np

from pm4py.util import exec_utils, vis_utils


class Parameters(Enum):
    WEIGHT_THRESHOLD = "weight_threshold"
    FORMAT = "format"


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
            - Parameters.WEIGHT_THRESHOLD -> the weight threshold to use in displaying the graph
            - Parameters.FORMAT -> format of the output image (png, svg ...)

    Returns
    -------------
    temp_file_name
        Name of a temporary file where the visualization is placed
    """
    import networkx as nx

    if parameters is None:
        parameters = {}

    weight_threshold = exec_utils.get_param_value(Parameters.WEIGHT_THRESHOLD, parameters, 0)
    format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")

    directed = metric_values[2]

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

    current_backend = copy(matplotlib.get_backend())
    matplotlib.use('Agg')
    from matplotlib import pyplot

    pyplot.clf()
    nx.draw(graph, with_labels=True, labels=labels, node_size=500, pos=nx.circular_layout(graph))
    pyplot.savefig(temp_file_name, bbox_inches="tight")
    pyplot.clf()

    matplotlib.use(current_backend)

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

    if vis_utils.check_visualization_inside_jupyter():
        vis_utils.view_image_in_jupyter(temp_file_name)
    else:
        vis_utils.open_opsystem_image_viewer(temp_file_name)


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
