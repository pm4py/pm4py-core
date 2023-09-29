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
import numpy as np
import json, logging
import importlib.util
from pm4py.util import exec_utils
from enum import Enum


class Parameters(Enum):
    GRAPH_POINTS = "graph_points"
    POINT_TO_SAMPLE = "points_to_sample"


def get_kde_caseduration(duration_values, parameters=None):
    """
    Gets the estimation of KDE density for the case durations calculated on the log/dataframe

    Parameters
    --------------
    duration_values
        Values of duration
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph

    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    if importlib.util.find_spec("scipy"):
        from scipy.stats import gaussian_kde

        if parameters is None:
            parameters = {}

        graph_points = exec_utils.get_param_value(Parameters.GRAPH_POINTS, parameters, 200)
        duration_values = sorted(duration_values)
        density = gaussian_kde(duration_values)
        xs1 = list(np.linspace(min(duration_values), max(duration_values), int(graph_points/2)))
        xs2 = list(np.geomspace(max(min(duration_values), 0.001), max(duration_values), int(graph_points/2)))
        xs = sorted(xs1 + xs2)

        return [xs, list(density(xs))]
    else:
        msg = "scipy is not available. graphs cannot be built!"
        logging.error(msg)
        raise Exception(msg)


def get_kde_caseduration_json(duration_values, parameters=None):
    """
    Gets the estimation of KDE density for the case durations calculated on the log/dataframe
    (expressed as JSON)

    Parameters
    --------------
    duration_values
        Values of duration
    parameters
        Possible parameters of the algorithm, including:
            graph_points: number of points to include in the graph

    Returns
    --------------
    json
        JSON representing the graph points
    """
    x, y = get_kde_caseduration(duration_values, parameters=parameters)

    ret = []
    for i in range(len(x)):
        ret.append((x[i], y[i]))

    return json.dumps(ret)


