from typing import Optional, Dict, Any
from pm4py.objects.bpmn.obj import BPMN
from pm4py.util import exec_utils, constants, vis_utils
from enum import Enum
from copy import copy
import shutil
import tempfile
import importlib.resources


class Parameters(Enum):
    ENCODING = "encoding"
    IFRAME_WIDTH = "iframe_width"
    IFRAME_HEIGHT = "iframe_height"
    LOCAL_JUPYTER_FILE_NAME = "local_jupyter_file_name"


def get_html_file_contents():
    file_path = 'pm4py/static/myfile.html'
    resource_path = importlib.resources.path("pm4py.visualization.bpmn.util", "dagrejs_base.html")
    with open(resource_path, 'r') as html_file:
        return html_file.read()


def apply(bpmn_graph: BPMN, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Visualizes a BPMN graph by rendering it inside a HTML/Javascript file

    Parameters
    --------------
    bpmn_graph
        BPMN graph
    parameters
        Parameters of the algorithm, including:
        - Parameters.ENCODING => the encoding of the HTML to be used

    Returns
    ---------------
    tmp_file_path
        Path to the HTML file
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)

    from pm4py.objects.bpmn.exporter.variants import etree as bpmn_xml_exporter
    export_parameters = copy(parameters)
    xml_stri = bpmn_xml_exporter.get_xml_string(bpmn_graph, parameters=export_parameters)
    xml_stri = xml_stri.decode(encoding).replace("\t", "").replace("\r", "").replace("\n", "")

    F = tempfile.NamedTemporaryFile(suffix=".html")
    F.close()

    F = open(F.name, "w", encoding=encoding)
    F.write(get_html_file_contents().replace("REPLACE", xml_stri))
    F.close()

    return F.name


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

    iframe_width = exec_utils.get_param_value(Parameters.IFRAME_WIDTH, parameters, 900)
    iframe_height = exec_utils.get_param_value(Parameters.IFRAME_HEIGHT, parameters, 600)
    local_jupyter_file_name = exec_utils.get_param_value(Parameters.LOCAL_JUPYTER_FILE_NAME, parameters, "jupyter_sna_vis.html")

    if vis_utils.check_visualization_inside_jupyter():
        from IPython.display import IFrame
        shutil.copyfile(temp_file_name, local_jupyter_file_name)
        iframe = IFrame(local_jupyter_file_name, width=iframe_width, height=iframe_height)
        from IPython.display import display
        return display(iframe)
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
