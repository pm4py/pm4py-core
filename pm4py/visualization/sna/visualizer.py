from pm4py.visualization.sna.versions import networkx, pyvis
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    NETWORKX = networkx
    PYVIS = pyvis


DEFAULT_VARIANT = Variants.NETWORKX


def apply(metric_values, parameters=None, variant=DEFAULT_VARIANT):
    """
    Perform SNA visualization starting from the Matrix Container object
    and the Resource-Resource matrix

    Parameters
    -------------
    metric_values
        Value of the metrics
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm to use, possible values:
            - Variants.NETWORKX
            - Variants.PYVIS

    Returns
    -------------
    temp_file_name
        Name of a temporary file where the visualization is placed
    """
    return exec_utils.get_variant(variant).apply(metric_values, parameters=parameters)


def view(temp_file_name, parameters=None, variant=DEFAULT_VARIANT):
    """
    View the SNA visualization on the screen

    Parameters
    -------------
    temp_file_name
        Temporary file name
    parameters
        Possible parameters of the algorithm
    """
    return exec_utils.get_variant(variant).view(temp_file_name, parameters=parameters)


def save(temp_file_name, dest_file, parameters=None, variant=DEFAULT_VARIANT):
    """
    Save the SNA visualization from a temporary file to a well-defined destination file

    Parameters
    -------------
    temp_file_name
        Temporary file name
    dest_file
        Destination file
    parameters
        Possible parameters of the algorithm
    """
    return exec_utils.get_variant(variant).save(temp_file_name, dest_file, parameters=parameters)
