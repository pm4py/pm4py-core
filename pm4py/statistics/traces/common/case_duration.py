from scipy.stats import gaussian_kde
import numpy as np
import json
import math


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
    if parameters is None:
        parameters = {}

    graph_points = parameters["graph_points"] if "graph_points" in parameters else 200
    duration_values = sorted(duration_values)
    density = gaussian_kde(duration_values)
    xs1 = list(np.linspace(min(duration_values), max(duration_values), graph_points/2))
    xs2 = list(np.geomspace(max(min(duration_values), 0.001), max(duration_values), graph_points/2))
    xs = sorted(xs1 + xs2)

    return [xs, list(density(xs))]


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


