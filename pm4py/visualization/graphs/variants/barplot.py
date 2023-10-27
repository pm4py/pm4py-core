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
from copy import copy
from enum import Enum

import matplotlib

from pm4py.util import exec_utils, constants
from pm4py.visualization.graphs.util import common
from typing import Optional, Dict, Any, Union, List


class Parameters(Enum):
    TITLE = "title"
    FORMAT = "format"
    X_AXIS = "x_axis"
    Y_AXIS = "y_axis"
    PYPLOT_FIGURE_KWARGS = "pylot_figure_kwargs"
    TRANSPARENT = "transparent"


def apply_plot(x: List[float], y: List[float], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> str:
    """
    Visualizes a barchar provided its x-axis and y-axis points

    Parameters
    -----------------
    x
        X-axis points
    y
        Y-axis points
    parameters
        Parameters

    Returns
    -----------------
    tmp_file_name
        Temporary file name
    """
    if parameters is None:
        parameters = {}

    title = exec_utils.get_param_value(Parameters.TITLE, parameters, "")
    format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    x_axis = exec_utils.get_param_value(Parameters.X_AXIS, parameters, "")
    y_axis = exec_utils.get_param_value(Parameters.Y_AXIS, parameters, "")
    pyplot_figure_kwargs = exec_utils.get_param_value(Parameters.PYPLOT_FIGURE_KWARGS, parameters, {})
    is_transp = exec_utils.get_param_value(Parameters.TRANSPARENT, parameters, True if constants.DEFAULT_BGCOLOR == "transparent" else False)

    filename = common.get_temp_file_name(format)

    current_backend = copy(matplotlib.get_backend())
    matplotlib.use('Agg')
    from matplotlib import pyplot

    pyplot.clf()
    fig = pyplot.figure(**pyplot_figure_kwargs)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.bar(x, y)
    pyplot.xlabel(x_axis)
    pyplot.xticks(rotation=90, fontsize=8)
    pyplot.ylabel(y_axis)
    pyplot.title(title)
    pyplot.savefig(filename, bbox_inches="tight", transparent=is_transp)
    pyplot.clf()

    matplotlib.use(current_backend)

    return filename
