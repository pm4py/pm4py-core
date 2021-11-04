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
import math
import os
import tempfile
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Union

import matplotlib as mpl
import matplotlib.cm as cm

from pm4py.util import exec_utils
from pm4py.util.colors import get_string_from_int_below_255


class Parameters(Enum):
    FORMAT = "format"
    ACT_DIVIDER_SPACE = "act_divider_space"
    DATE_DIVIDER_SPACE = "date_divider_space"
    OVERALL_LENGTH_X = "overall_length_x"
    N_DIV_DATES = "n_div_dates"
    PERC_PATHS = "perc_paths"


def give_color_to_line(dir: float) -> str:
    """
    Gives a gradient color to the line

    Parameters
    ----------------
    dir
        Intensity of the difference (number between 0 and 1; 0=min difference, 1=max difference)

    Returns
    ----------------
    color
        Gradient color
    """
    dir = 0.5 + 0.5 * dir
    norm = mpl.colors.Normalize(vmin=0, vmax=1)
    nodes = [0.0, 0.01, 0.25, 0.4, 0.45, 0.55, 0.75, 0.99, 1.0]
    colors = ["deepskyblue", "skyblue", "lightcyan", "lightgray", "gray", "lightgray", "mistyrose", "salmon", "tomato"]
    cmap = mpl.colors.LinearSegmentedColormap.from_list("mycmap2", list(zip(nodes, colors)))
    # cmap = cm.plasma
    m = cm.ScalarMappable(norm=norm, cmap=cmap)
    rgba = m.to_rgba(dir)
    r = get_string_from_int_below_255(math.ceil(rgba[0] * 255.0))
    g = get_string_from_int_below_255(math.ceil(rgba[1] * 255.0))
    b = get_string_from_int_below_255(math.ceil(rgba[2] * 255.0))
    return "#" + r + g + b


def apply(perf_spectrum: Dict[str, Any], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> str:
    """
    Construct the performance spectrum visualization

    Parameters
    ----------------
    perf_spectrum
        Performance spectrum
    parameters
        Parameters of the algorithm, including:
        - Parameters.FORMAT => format of the output (svg, png, ...)
        - Parameters.ACT_DIVIDER_SPACE => space between the activities in the spectrum
        - Parameters.DATE_DIVIDER_SPACE => space between the lines and the dates
        - Parmaeters.OVERALL_LENGTH_X => length of the X-line
        - Parameters.N_DIV_DATES => specifies the number of intermediate dates reported
        - Parameters.PERC_PATHS => (if provided) filter the (overall) most long paths

    Returns
    ---------------
    file_path
        Path containing the visualization
    """
    if parameters is None:
        parameters = {}

    format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    act_divider = exec_utils.get_param_value(Parameters.ACT_DIVIDER_SPACE, parameters, 3.0)
    date_divider = exec_utils.get_param_value(Parameters.DATE_DIVIDER_SPACE, parameters, 1.0)
    overall_length = exec_utils.get_param_value(Parameters.OVERALL_LENGTH_X, parameters, 10.0)
    n_div = exec_utils.get_param_value(Parameters.N_DIV_DATES, parameters, 2)
    perc_paths = exec_utils.get_param_value(Parameters.PERC_PATHS, parameters, 1.0)

    output_file_gv = tempfile.NamedTemporaryFile(suffix=".gv")
    output_file_gv.close()

    output_file_img = tempfile.NamedTemporaryFile(suffix="." + format)
    output_file_img.close()

    lines = []
    lines.append("graph G {")

    min_x = min(x[0] for x in perf_spectrum["points"])
    max_x = max(x[-1] for x in perf_spectrum["points"])
    all_diffs = [x[i + 1] - x[i] for x in perf_spectrum["points"] for i in range(len(x) - 1)]
    min_diff = min(all_diffs)
    max_diff = max(all_diffs)

    points = sorted(perf_spectrum["points"], key=lambda x: x[-1] - x[0], reverse=True)
    points = points[:math.ceil(perc_paths * len(points))]

    for polyline in points:
        this_pts = []
        for i, p in enumerate(polyline):
            p_id = "n" + str(uuid.uuid4()).replace("-", "") + "e"
            first_coord = (p - min_x) / (max_x - min_x) * overall_length
            second_coord = act_divider * (len(perf_spectrum["list_activities"]) - i - 1)
            lines.append(
                "%s [label=\"\", pos=\"%.10f,%.10f!\", shape=none, width=\"0px\", height=\"0px\"];" % (p_id, first_coord, second_coord))
            this_pts.append(p_id)
        for i in range(len(this_pts) - 1):
            diff = polyline[i + 1] - polyline[i]
            color = give_color_to_line((diff - min_diff) / (max_diff - min_diff))
            lines.append("%s -- %s [ color=\"%s\" ];" % (this_pts[i], this_pts[i + 1], color))

    for i, act in enumerate(perf_spectrum["list_activities"]):
        second_coord = act_divider * (len(perf_spectrum["list_activities"]) - i - 1)
        a_id = "n" + str(uuid.uuid4()).replace("-", "") + "e"
        lines.append("%s [label=\"%s\", pos=\"%.10f,%.10f!\", shape=none, width=\"0px\", height=\"0px\"];" % (
        a_id, act, overall_length, second_coord))
        s_id = "n" + str(uuid.uuid4()).replace("-", "") + "e"
        lines.append("%s [label=\"\", pos=\"0,%.10f!\", shape=none, width=\"0px\", height=\"0px\"];" % (s_id, second_coord))
        lines.append("%s -- %s [ color=\"black\" ];" % (s_id, a_id))
        if i == len(perf_spectrum["list_activities"]) - 1:
            for j in range(n_div + 1):
                pos = float(j * overall_length) / float(n_div)
                tst = min_x + float(j) / float(n_div) * (max_x - min_x)
                dt = datetime.fromtimestamp(tst)
                n_id = "n" + str(uuid.uuid4()).replace("-", "") + "e"
                lines.append("%s [label=\"%s\", pos=\"%.10f,%.10f!\", shape=none, width=\"0px\", height=\"0px\"];" % (
                n_id, str(dt), pos, second_coord - date_divider))

    lines.append("}")
    lines = "\n".join(lines)

    F = open(output_file_gv.name, "w")
    F.write(lines)
    F.close()

    os.system("neato -T" + format + " " + output_file_gv.name + " > " + output_file_img.name)

    return output_file_img.name
