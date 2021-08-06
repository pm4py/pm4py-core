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
import matplotlib
from copy import copy

from pm4py.visualization.graphs.util import common
from pm4py.util import exec_utils
from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple, List


class Parameters(Enum):
    TITLE = "title"
    FORMAT = "format"
    X_AXIS = "x_axis"
    Y_AXIS = "y_axis"


ATTRIBUTE_LABEL = "Attribute value"
DENSITY_LABEL = "Density"
GRAPH_DEFAULT_TITLE = "Attribute Distribution"


def apply_plot(x: List[float], y: List[float], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> str:
    """
    Plot (non-logarithmic way) the graph with axis values contained in x and y

    Parameters
    ------------
    x
        Values for x-axis
    y
        Values for y-axis
    parameters
        Parameters of the algorithm, including:
            Parameters.FORMAT -> Format of the target image
            Parameters.TITLE -> Title of the image

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    if parameters is None:
        parameters = {}

    format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    title = exec_utils.get_param_value(Parameters.TITLE, parameters, GRAPH_DEFAULT_TITLE)
    x_axis = exec_utils.get_param_value(Parameters.X_AXIS, parameters, ATTRIBUTE_LABEL)
    y_axis = exec_utils.get_param_value(Parameters.Y_AXIS, parameters, DENSITY_LABEL)

    filename = common.get_temp_file_name(format)

    current_backend = copy(matplotlib.get_backend())
    matplotlib.use('Agg')
    from matplotlib import pyplot

    pyplot.clf()
    pyplot.plot(x, y)
    pyplot.xlabel(x_axis)
    pyplot.ylabel(y_axis)
    pyplot.savefig(filename, bbox_inches="tight", transparent=True)
    pyplot.title(title)
    pyplot.clf()

    matplotlib.use(current_backend)

    return filename


def apply_semilogx(x: List[float], y: List[float], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> str:
    """
    Plot (semi-logarithmic way) the graph with axis values contained in x and y

    Parameters
    ------------
    x
        Values for x-axis
    y
        Values for y-axis
    parameters
        Parameters of the algorithm, including:
            Parameters.FORMAT -> Format of the target image
            Parameters.TITLE -> Title of the image

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    if parameters is None:
        parameters = {}

    format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    title = exec_utils.get_param_value(Parameters.TITLE, parameters, GRAPH_DEFAULT_TITLE)

    filename = common.get_temp_file_name(format)

    current_backend = copy(matplotlib.get_backend())
    matplotlib.use('Agg')
    from matplotlib import pyplot

    pyplot.clf()
    pyplot.semilogx(x, y)
    pyplot.xlabel(ATTRIBUTE_LABEL)
    pyplot.ylabel(DENSITY_LABEL)
    pyplot.savefig(filename, bbox_inches="tight", transparent=True)
    pyplot.title(title)
    pyplot.clf()

    matplotlib.use(current_backend)

    return filename
