import base64

MAX_EDGE_PENWIDTH_GRAPHVIZ = 2.6
MIN_EDGE_PENWIDTH_GRAPHVIZ = 1.0


def human_readable_stat(c):
    """
    Transform a timedelta expressed in seconds into a human readable string

    Parameters
    ----------
    c
        Timedelta expressed in seconds

    Returns
    ----------
    string
        Human readable string
    """
    c = int(float(c))
    years = c // 31104000
    months = c // 2592000
    days = c // 86400
    hours = c // 3600 % 24
    minutes = c // 60 % 60
    seconds = c % 60
    if years > 0:
        return str(years) + "Y"
    if months > 0:
        return str(months) + "MO"
    if days > 0:
        return str(days) + "D"
    if hours > 0:
        return str(hours) + "h"
    if minutes > 0:
        return str(minutes) + "m"
    return str(seconds) + "s"


def get_arc_penwidth(arc_measure, min_arc_measure, max_arc_measure):
    """
    Calculate arc width given the current arc measure value, the minimum arc measure value and the
    maximum arc measure value

    Parameters
    -----------
    arc_measure
        Current arc measure value
    min_arc_measure
        Minimum measure value among all arcs
    max_arc_measure
        Maximum measure value among all arcs

    Returns
    -----------
    penwidth
        Current arc width in the graph
    """
    return MIN_EDGE_PENWIDTH_GRAPHVIZ + (MAX_EDGE_PENWIDTH_GRAPHVIZ - MIN_EDGE_PENWIDTH_GRAPHVIZ) * (
                arc_measure - min_arc_measure) / (max_arc_measure - min_arc_measure + 0.00001)


def get_trans_freq_color(trans_count, min_trans_count, max_trans_count):
    """
    Gets transition frequency color

    Parameters
    ----------
    trans_count
        Current transition count
    min_trans_count
        Minimum transition count
    max_trans_count
        Maximum transition count

    Returns
    ----------
    color
        Frequency color for visible transition
    """
    trans_base_color = int(255 - 100 * (trans_count - min_trans_count) / (max_trans_count - min_trans_count + 0.00001))
    trans_base_color_hex = str(hex(trans_base_color))[2:].upper()
    return "#" + trans_base_color_hex + trans_base_color_hex + "FF"


def get_base64_from_gviz(gviz):
    """
    Get base 64 from string content of the file

    Parameters
    -----------
    gviz
        Graphviz diagram

    Returns
    -----------
    base64
        Base64 string
    """
    render = gviz.render(view=False)
    with open(render, "rb") as f:
        return base64.b64encode(f.read())


def get_base64_from_file(temp_file):
    """
    Get base 64 from string content of the file

    Parameters
    -----------
    temp_file
        Temporary file path

    Returns
    -----------
    base64
        Base64 string
    """
    with open(temp_file, "rb") as f:
        return base64.b64encode(f.read())
