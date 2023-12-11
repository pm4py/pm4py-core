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
import json, logging
import importlib.util

from pm4py.util.points_subset import pick_chosen_points_list
from pm4py.util import exec_utils, pandas_utils, constants
from enum import Enum


class Parameters(Enum):
    GRAPH_POINTS = "graph_points"
    POINT_TO_SAMPLE = "points_to_sample"


def get_sorted_attributes_list(attributes):
    """
    Gets sorted attributes list

    Parameters
    ----------
    attributes
        Dictionary of attributes associated with their count

    Returns
    ----------
    listact
        Sorted end attributes list
    """
    listattr = []
    for a in attributes:
        listattr.append([a, attributes[a]])
    listattr = sorted(listattr, key=lambda x: x[1], reverse=True)
    return listattr


def get_attributes_threshold(alist, decreasing_factor, min_activity_count=1, max_activity_count=25):
    """
    Get attributes cutting threshold

    Parameters
    ----------
    alist
        Sorted attributes list
    decreasing_factor
        Decreasing factor of the algorithm
    min_activity_count
        Minimum number of activities to include
    max_activity_count
        Maximum number of activities to include

    Returns
    ---------
    threshold
        Activities cutting threshold
    """
    index = max(0, min(min_activity_count - 1, len(alist) - 1))
    threshold = alist[index][1]
    index = index + 1
    for i in range(index, len(alist)):
        value = alist[i][1]
        if value > threshold * decreasing_factor:
            threshold = value
        if i >= max_activity_count:
            break
    return threshold


def get_kde_numeric_attribute(values, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values

    Parameters
    -------------
    values
        Values of the numeric attribute value
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
    if importlib.util.find_spec("scipy") and importlib.util.find_spec("numpy"):
        from scipy.stats import gaussian_kde
        import numpy as np
        import pandas as pd

        if parameters is None:
            parameters = {}

        graph_points = exec_utils.get_param_value(Parameters.GRAPH_POINTS, parameters, 200)
        values = sorted(values)
        density = gaussian_kde(values)

        xs1 = list(np.linspace(min(values), max(values), int(graph_points / 2)))
        xs2 = list(np.geomspace(max(min(values), 0.000001), max(values), int(graph_points / 2)))
        xs = sorted(xs1 + xs2)

        return [xs, list(density(xs))]
    else:
        msg = "scipy is not available. graphs cannot be built!"
        logging.error(msg)
        raise Exception(msg)


def get_kde_numeric_attribute_json(values, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values
    (expressed as JSON)

    Parameters
    --------------
    values
        Values of the numeric attribute value
    parameters
        Possible parameters of the algorithm, including:
            graph_points: number of points to include in the graph

    Returns
    --------------
    json
        JSON representing the graph points
    """
    x, y = get_kde_numeric_attribute(values, parameters=parameters)

    ret = []
    for i in range(len(x)):
        ret.append((x[i], y[i]))

    return json.dumps(ret)


def get_kde_date_attribute(values, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values

    Parameters
    -------------
    values
        Values of the date attribute value
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
    if importlib.util.find_spec("scipy") and importlib.util.find_spec("numpy"):
        from scipy.stats import gaussian_kde
        import numpy as np
        import pandas as pd

        if parameters is None:
            parameters = {}

        graph_points = exec_utils.get_param_value(Parameters.GRAPH_POINTS, parameters, 200)
        points_to_sample = exec_utils.get_param_value(Parameters.POINT_TO_SAMPLE, parameters, 400)

        red_values = pick_chosen_points_list(points_to_sample, values)
        int_values = sorted(
            [x.replace(tzinfo=None).timestamp() for x in red_values])
        density = gaussian_kde(int_values)
        xs = np.linspace(min(int_values), max(int_values), graph_points)
        xs_transf = pd.to_datetime(xs * 10 ** 9, unit="ns")

        return [xs_transf, density(xs)]
    else:
        msg = "scipy is not available. graphs cannot be built!"
        logging.error(msg)
        raise Exception(msg)


def get_kde_date_attribute_json(values, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values
    (expressed as JSON)

    Parameters
    --------------
    values
        Values of the date attribute value
    parameters
        Possible parameters of the algorithm, including:
            graph_points: number of points to include in the graph

    Returns
    --------------
    json
        JSON representing the graph points
    """
    x, y = get_kde_date_attribute(values, parameters=parameters)

    ret = []
    for i in range(len(x)):
        ret.append((x[i].replace(tzinfo=None).timestamp(), y[i]))

    return json.dumps(ret)
