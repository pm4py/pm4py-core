import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot

from pm4py.visualization.graphs.util import common

ATTRIBUTE_LABEL = "Attribute value"
DENSITY_LABEL = "Density"
GRAPH_DEFAULT_TITLE = "Attribute Distribution"

def apply_plot(x, y, parameters=None):
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
            format -> Format of the target image

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    if parameters is None:
        parameters = {}

    format = parameters["format"] if "format" in parameters else "png"
    title = parameters["title"] if "title" in parameters else GRAPH_DEFAULT_TITLE

    filename = common.get_temp_file_name(format)

    pyplot.clf()
    pyplot.plot(x, y)
    pyplot.xlabel(ATTRIBUTE_LABEL)
    pyplot.ylabel(DENSITY_LABEL)
    pyplot.savefig(filename, bbox_inches="tight")
    pyplot.title(title)
    pyplot.clf()

    return filename


def apply_semilogx(x, y, parameters=None):
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
            format -> Format of the target image

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    if parameters is None:
        parameters = {}

    format = parameters["format"] if "format" in parameters else "png"
    title = parameters["title"] if "title" in parameters else GRAPH_DEFAULT_TITLE

    filename = common.get_temp_file_name(format)

    pyplot.clf()
    pyplot.semilogx(x, y)
    pyplot.xlabel(ATTRIBUTE_LABEL)
    pyplot.ylabel(DENSITY_LABEL)
    pyplot.savefig(filename, bbox_inches="tight")
    pyplot.title(title)
    pyplot.clf()

    return filename