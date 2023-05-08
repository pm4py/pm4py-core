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

from pm4py.util import constants, vis_utils
from tempfile import NamedTemporaryFile
from enum import Enum
from pm4py.util import exec_utils
import shutil


class Parameters(Enum):
    IFRAME_WIDTH = "iframe_width"
    IFRAME_HEIGHT = "iframe_height"
    LOCAL_JUPYTER_FILE_NAME = "local_jupyter_file_name"


def form_html(gviz, name=None):
    """
    Forms the HTML page using GraphvizJS

    Parameters
    -----------
    gviz
        GraphViz diagram
    name
        (optional) path where the GraphViz output should be saved

    Returns
    -----------
    name
        Path where the GraphvizJS output is saved
    """
    if name is None:
        html_file = NamedTemporaryFile(suffix=".html")
        html_file.close()
        name = html_file.name

    F = open(name, "w")
    F.write('<html><head>')
    F.write('<script type="text/javascript" src="'+constants.JQUERY_LINK+'"></script>')
    F.write('<script type="text/javascript" src="'+constants.GRAPHVIZJS_LINK+'"></script>')
    F.write('</head><body><div id="container"></div><script type="text/javascript">let gv = `\n')
    F.write(str(gviz))
    F.write('`;let svgXml = Viz(gv, { format: "svg"});document.getElementById("container").innerHTML = svgXml;</script></body></html>')
    F.close()

    return name


def save(gviz, output_file_path, parameters=None):
    """
    Saves the diagram in HTML format

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    if parameters is None:
        parameters = {}

    form_html(gviz, output_file_path)


def view(gviz, parameters=None):
    """
    View the diagram in HTML format

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    if parameters is None:
        parameters = {}

    iframe_width = exec_utils.get_param_value(Parameters.IFRAME_WIDTH, parameters, 900)
    iframe_height = exec_utils.get_param_value(Parameters.IFRAME_HEIGHT, parameters, 600)
    local_jupyter_file_name = exec_utils.get_param_value(Parameters.LOCAL_JUPYTER_FILE_NAME, parameters, "jupyter_html_vis.html")

    temp_file_name = form_html(gviz)

    if vis_utils.check_visualization_inside_jupyter():
        from IPython.display import IFrame
        shutil.copyfile(temp_file_name, local_jupyter_file_name)
        iframe = IFrame(local_jupyter_file_name, width=iframe_width, height=iframe_height)
        from IPython.display import display
        return display(iframe)
    else:
        vis_utils.open_opsystem_image_viewer(temp_file_name)
