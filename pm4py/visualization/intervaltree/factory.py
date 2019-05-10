from pm4py.visualization.intervaltree.versions import classic
from pm4py.visualization.intervaltree.util.common import save, view

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(tree_distr_points, variant="classic", parameters=None):
    """
    Visualize the interval tree distribution over time

    Parameters
    ------------
    tree_points
        Points of the interval tree
    variant
        Variant of the algorithm, possible values: classic
    parameters
        Parameters of the algorithm including: format, title

    Returns
    ------------
    filename
        Path to the file that hosts the image representing the interval tree
    """
    if parameters is None:
        parameters = {}

    return VERSIONS[variant](tree_distr_points, parameters=parameters)
