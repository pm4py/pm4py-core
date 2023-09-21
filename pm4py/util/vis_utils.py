'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import base64
import os
import subprocess
import sys
from typing import Optional, Dict


MAX_EDGE_PENWIDTH_GRAPHVIZ = 2.6
MIN_EDGE_PENWIDTH_GRAPHVIZ = 1.0


def human_readable_stat(timedelta, stat_locale: Optional[Dict[str, str]] = None) -> str:
    """
    Transform a timedelta into a human readable string

    Parameters
    ----------
    timedelta
        Timedelta

    Returns
    ----------
    string
        Human readable string
    """
    if stat_locale is None:
        stat_locale = {}

    c = int(float(timedelta))
    years = c // 31104000
    months = c // 2592000
    days = c // 86400
    hours = c // 3600 % 24
    minutes = c // 60 % 60
    seconds = c % 60
    if years > 0:
        return str(years) + stat_locale.get("year", "Y")
    elif months > 0:
        return str(months) + stat_locale.get("month", "MO")
    elif days > 0:
        return str(days) + stat_locale.get("day", "D")
    elif hours > 0:
        return str(hours) + stat_locale.get("hour", "h")
    elif minutes > 0:
        return str(minutes) + stat_locale.get("minute", "m")
    elif seconds > 0:
        return str(seconds) + stat_locale.get("second", "s")
    else:
        c = int(float(timedelta*1000))
        if c > 0:
            return str(c) + stat_locale.get("millisecond", "ms")
        else:
            return str(int(float(timedelta * 10**9))) + stat_locale.get("nanosecond", "ns")


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


def check_visualization_inside_jupyter():
    """
    Checks if the visualization of the model is performed
    inside a Jupyter notebook
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell" or shell == "Shell":
            return True
        else:
            return False
    except NameError:
        return False


def view_image_in_jupyter(file_name):
    """
    Visualizes a picture inside the Jupyter notebooks

    Parameters
    -------------
    file_name
        Name of the file
    """
    from IPython.display import Image
    image = Image(file_name)
    from IPython.display import display
    return display(image)


def open_opsystem_image_viewer(file_name):
    """
    Visualizes a picture using the image viewer of the operating system

    Parameters
    -------------
    file_name
        Name of the file
    """
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', file_name))
    elif os.name == 'nt':  # For Windows
        os.startfile(file_name)
    elif os.name == 'posix':  # For Linux, Mac, etc.
        subprocess.call(('xdg-open', file_name))


def get_corr_hex(num):
    """
    Gets correspondence between a number
    and an hexadecimal string

    Parameters
    -------------
    num
        Number

    Returns
    -------------
    hex_string
        Hexadecimal string
    """
    if num < 10:
        return str(int(num))
    elif num < 11:
        return "A"
    elif num < 12:
        return "B"
    elif num < 13:
        return "C"
    elif num < 14:
        return "D"
    elif num < 15:
        return "E"
    elif num < 16:
        return "F"
