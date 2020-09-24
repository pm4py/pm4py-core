from pm4py.visualization.graphs.versions import cases, attributes, dates
from pm4py.visualization.graphs.util.common import save, view, matplotlib_view
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    CASES = cases
    ATTRIBUTES = attributes
    DATES = dates


DEFAULT_VARIANT = Variants.CASES


def apply(x, y, parameters=None, variant=DEFAULT_VARIANT):
    """
    Method to plot (non-logarithmic way) the graph with axis values contained in x and y

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
    variant
        Variant of the algorithm to apply, including:
            - Variants.CASES
            - Variants.ATTRIBUTES
            - Variants.DATES

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    return exec_utils.get_variant(variant).apply_plot(x, y, parameters=parameters)


def apply_plot(x, y, parameters=None, variant=DEFAULT_VARIANT):
    """
    Method to plot (non-logarithmic way) the graph with axis values contained in x and y

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
    variant
        Variant of the algorithm to apply, including:
            - Variants.CASES
            - Variants.ATTRIBUTES
            - Variants.DATES

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    return exec_utils.get_variant(variant).apply_plot(x, y, parameters=parameters)


def apply_semilogx(x, y, parameters=None, variant=DEFAULT_VARIANT):
    """
    Method to plot (semi-logarithmic way) the graph with axis values contained in x and y

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
    variant
        Variant of the algorithm to apply, including:
            - Variants.CASES
            - Variants.ATTRIBUTES
            - Variants.DATES

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    return exec_utils.get_variant(variant).apply_semilogx(x, y, parameters=parameters)
