import shutil
import tempfile
from enum import Enum

from pm4py.util import exec_utils, vis_utils
from pm4py.objects.org.sna.obj import SNA


class Parameters(Enum):
    WEIGHT_THRESHOLD = "weight_threshold"


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


def apply(sna: SNA, parameters=None):
    """
    Perform SNA visualization starting from the Matrix Container object
    and the Resource-Resource matrix

    Parameters
    -------------
    sna
        Value of the metrics
    parameters
        Possible parameters of the algorithm, including:
            - Parameters.WEIGHT_THRESHOLD -> the weight threshold to use in displaying the graph

    Returns
    -------------
    temp_file_name
        Name of a temporary file where the visualization is placed
    """
    from pyvis.network import Network

    if parameters is None:
        parameters = {}

    weight_threshold = exec_utils.get_param_value(Parameters.WEIGHT_THRESHOLD, parameters, 0)
    directed = sna.is_directed

    temp_file_name = get_temp_file_name("html")

    got_net = Network(height="750px", width="100%", bgcolor="black", font_color="#3de975", directed=directed)
    # set the physics layout of the network
    got_net.barnes_hut()

    for c, w in sna.connections.items():
        if w >= weight_threshold:
            src = c[0]  # convert ids to labels
            dst = c[1]

            # I have to add some options here, there is no parameter
            highlight = {'border': "#3de975", 'background': "#41e9df"}
            # color = {'border': "#000000", 'background': "#123456"}
            got_net.add_node(src, src, title=src, labelHighlightBold=True, color={'highlight': highlight})
            got_net.add_node(dst, dst, title=dst, labelHighlightBold=True, color={'highlight': highlight})
            got_net.add_edge(src, dst, value=w, title=w)

    neighbor_map = got_net.get_adj_list()

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

    F = open(temp_file_name, "w")
    F.write(got_net.generate_html())
    F.close()
    
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
        raise Exception("pyvis visualization not working inside Jupyter notebooks")
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
