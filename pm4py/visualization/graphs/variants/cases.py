import matplotlib
from copy import copy

from pm4py.visualization.graphs.util import common
from pm4py.util import exec_utils, constants
from enum import Enum
from typing import Optional, Dict, Any, Union, List


class Parameters(Enum):
    TITLE = "title"
    FORMAT = "format"
    X_AXIS = "x_axis"
    Y_AXIS = "y_axis"
    PYPLOT_PLOT_KWARGS = "pylot_plot_kwargs"
    TRANSPARENT = "transparent"


CASE_DURATION_LABEL = "Case duration"
DENSITY_LABEL = "Density"
GRAPH_DEFAULT_TITLE = "Case Duration"


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
    x_axis = exec_utils.get_param_value(Parameters.X_AXIS, parameters, CASE_DURATION_LABEL)
    y_axis = exec_utils.get_param_value(Parameters.Y_AXIS, parameters, DENSITY_LABEL)
    pyplot_plot_kwargs = exec_utils.get_param_value(Parameters.PYPLOT_PLOT_KWARGS, parameters, {})
    is_transp = exec_utils.get_param_value(Parameters.TRANSPARENT, parameters, True if constants.DEFAULT_BGCOLOR == "transparent" else False)

    filename = common.get_temp_file_name(format)

    current_backend = copy(matplotlib.get_backend())
    matplotlib.use('Agg')
    from matplotlib import pyplot

    pyplot.clf()
    pyplot.plot(x, y, **pyplot_plot_kwargs)
    pyplot.xlabel(x_axis)
    pyplot.ylabel(y_axis)
    pyplot.title(title)
    pyplot.savefig(filename, bbox_inches="tight", transparent=is_transp)
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
    pyplot_plot_kwargs = exec_utils.get_param_value(Parameters.PYPLOT_PLOT_KWARGS, parameters, {})
    is_transp = exec_utils.get_param_value(Parameters.TRANSPARENT, parameters, True if constants.DEFAULT_BGCOLOR == "transparent" else False)

    filename = common.get_temp_file_name(format)

    current_backend = copy(matplotlib.get_backend())
    matplotlib.use('Agg')
    from matplotlib import pyplot

    pyplot.clf()
    pyplot.semilogx(x, y, **pyplot_plot_kwargs)
    pyplot.xlabel(CASE_DURATION_LABEL)
    pyplot.ylabel(DENSITY_LABEL)
    pyplot.title(title)
    pyplot.savefig(filename, bbox_inches="tight", transparent=is_transp)
    pyplot.clf()

    matplotlib.use(current_backend)

    return filename
