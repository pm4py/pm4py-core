from pm4py.visualization.sna.versions import networkx, pyvis

NETWORKX = "networkx"
PYVIS = "pyvis"

VERSIONS_APPLY = {NETWORKX: networkx.apply, PYVIS: pyvis.apply}
VERSIONS_VIEW = {NETWORKX: networkx.view, PYVIS: pyvis.view}
VERSIONS_SAVE = {NETWORKX: networkx.save, PYVIS: pyvis.save}


def apply(metric_values, parameters=None, variant=NETWORKX):
    """
    Perform SNA visualization starting from the Matrix Container object
    and the Resource-Resource matrix

    Parameters
    -------------
    metric_values
        Value of the metrics
    parameters
        Possible parameters of the algorithm, including:
            weight_threshold: the weight threshold to use in displaying the graph
            directed: indicates if the graph has to be drawn directed
            format: format of the output image (png, svg ...)

    Returns
    -------------
    temp_file_name
        Name of a temporary file where the visualization is placed
    """
    return VERSIONS_APPLY[variant](metric_values, parameters=parameters)


def view(temp_file_name, parameters=None, variant=NETWORKX):
    """
    View the SNA visualization on the screen

    Parameters
    -------------
    temp_file_name
        Temporary file name
    parameters
        Possible parameters of the algorithm
    """
    return VERSIONS_VIEW[variant](temp_file_name, parameters=parameters)


def save(temp_file_name, dest_file, parameters=None, variant=NETWORKX):
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
    return VERSIONS_SAVE[variant](temp_file_name, dest_file, parameters=parameters)
