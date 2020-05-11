import deprecation

from pm4py.visualization.graphs.versions import cases, attributes, dates
from pm4py.visualization.graphs.util.common import save, view


CASES = "cases"
ATTRIBUTES = "attributes"
DATES = "dates"

VERSIONS_PLOT = {CASES: cases.apply_plot, ATTRIBUTES: attributes.apply_plot, DATES: dates.apply_plot}
VERSIONS_SEMILOGX = {CASES: cases.apply_semilogx, ATTRIBUTES: attributes.apply_semilogx, DATES: dates.apply_semilogx}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use visualizer module instead.')
def apply(x, y, parameters=None, variant=CASES):
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
            format -> Format of the target image
    variant
        Variant of the algorithm to apply, including: cases

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    return apply_plot(x, y, parameters=parameters, variant=variant)

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use visualizer module instead.')
def apply_plot(x, y, parameters=None, variant=CASES):
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
            format -> Format of the target image
    variant
        Variant of the algorithm to apply, including: cases

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    return VERSIONS_PLOT[variant](x, y, parameters=parameters)

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use visualizer module instead.')
def apply_semilogx(x, y, parameters=None, variant=CASES):
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
            format -> Format of the target image
    variant
        Variant of the algorithm to apply, including: cases

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    return VERSIONS_SEMILOGX[variant](x, y, parameters=parameters)
