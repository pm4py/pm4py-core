import json

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

from pm4py.util.points_subset import pick_chosen_points_list


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
    if parameters is None:
        parameters = {}

    graph_points = parameters["graph_points"] if "graph_points" in parameters else 200
    values = sorted(values)
    density = gaussian_kde(values)

    xs1 = list(np.linspace(min(values), max(values), graph_points / 2))
    xs2 = list(np.geomspace(max(min(values), 0.000001), max(values), graph_points / 2))
    xs = sorted(xs1 + xs2)

    return [xs, list(density(xs))]


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
    if parameters is None:
        parameters = {}

    graph_points = parameters["graph_points"] if "graph_points" in parameters else 200
    points_to_sample = parameters["points_to_sample"] if "points_to_sample" in parameters else 400
    red_values = pick_chosen_points_list(points_to_sample, values)
    int_values = sorted(
        [x.replace(tzinfo=None).timestamp() for x in red_values])
    density = gaussian_kde(int_values)
    xs = np.linspace(min(int_values), max(int_values), graph_points)
    xs_transf = pd.to_datetime(xs * 10 ** 9)

    return [xs_transf, density(xs)]


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
