import matplotlib

matplotlib.use('Agg')

from matplotlib import pyplot

from intervaltree import IntervalTree
from pm4py.algo.other.intervaltree.representation import factory as representation_factory
from pm4py.visualization.intervaltree.util import common
from datetime import datetime


GRAPH_DEFAULT_TITLE = "Attribute Distribution"
X_LABEL = "Time interval"
Y_LABEL = "Count of intervals"


def apply(tree_points, parameters=None):
    """
    Visualize the interval tree distribution over time

    Parameters
    ------------
    tree_points
        Points of the interval tree
    parameters
        Parameters of the algorithm including: format, title

    Returns
    ------------
    filename
        Path to the file that hosts the image representing the interval tree
    """
    if parameters is None:
        parameters = {}

    if type(tree_points) is IntervalTree:
        tree_points = representation_factory.apply(tree_points)

    format = parameters["format"] if "format" in parameters else "png"
    title = parameters["title"] if "title" in parameters else GRAPH_DEFAULT_TITLE

    filename = common.get_temp_file_name(format)

    x = [datetime.fromtimestamp(z[0]) for z in tree_points]
    y = [z[1] for z in tree_points]

    pyplot.clf()
    pyplot.plot(x, y)
    pyplot.xlabel(X_LABEL)
    pyplot.ylabel(Y_LABEL)
    pyplot.xticks(rotation=90)
    pyplot.savefig(filename, bbox_inches="tight")
    pyplot.title(title)
    pyplot.clf()

    return filename
