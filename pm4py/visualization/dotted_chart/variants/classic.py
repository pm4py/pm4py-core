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
import datetime
import os
import tempfile
import uuid
from enum import Enum
from random import randint
from typing import List, Any, Tuple, Dict, Optional, Union

from pm4py.util import exec_utils


class Parameters(Enum):
    FORMAT = "format"
    DOT_SIZE = "dot_size"


def __build_unique_values(points_list: List[Any]) -> List[Any]:
    """
    Finds the unique values among the attribute values

    Parameters
    ----------------
    points_list
        Points list

    Returns
    ----------------
    list_unq_values
        List of unique values for each attribute
    """
    unique_values = []
    for i in range(len(points_list[0])):
        unique_values.append(set())
        for j in range(len(points_list)):
            unique_values[-1].add(points_list[j][i])
        unique_values[-1] = sorted(list(unique_values[-1]))
    return unique_values


def __build_corr_dict(unique_values: List[Any]) -> Tuple[List[Any], List[str]]:
    """
    Builds the correspondence between unique values and positions in the graph

    Parameters
    ----------------
    unique_values
        List of unique values for each attribute

    Returns
    ----------------
    corr_dict
        Correspondence between unique values and positions
    attr_type
        A list containing the attribute type for each attribute
    """
    corr_dict = []
    attr_type = []
    for i in range(len(unique_values)):
        corr_dict.append({})
        if isinstance(unique_values[i][0], datetime.datetime):
            min_t = unique_values[i][0].timestamp()
            max_t = unique_values[i][-1].timestamp()
            for idx, v in enumerate(unique_values[i]):
                corr_dict[-1][v] = 1.0 / len(unique_values[i]) + (len(unique_values[i]) - 1) / len(unique_values[i]) * (
                        v.timestamp() - min_t) / (max_t - min_t + 0.00001)
            attr_type.append("date")
        elif isinstance(unique_values[i][0], float) or isinstance(unique_values[i][0], int):
            min_t = unique_values[i][0]
            max_t = unique_values[i][-1]
            for idx, v in enumerate(unique_values[i]):
                corr_dict[-1][v] = 1.0 / len(unique_values[i]) + (len(unique_values[i]) - 1) / len(unique_values[i]) * (
                        v - min_t) / (max_t - min_t + 0.00001)
            attr_type.append("number")
        else:
            for idx, v in enumerate(unique_values[i]):
                corr_dict[-1][v] = float(idx + 1) / float(len(unique_values[i]) + 1)
            attr_type.append("str")
    return corr_dict, attr_type


def __build_color_dict(third_values: List[Any]) -> Dict[Any, str]:
    """
    Builds the color map for the values of the third attribute

    Parameters
    ---------------
    third_values
        Unique values of the third attribute

    Returns
    ---------------
    cmap
        Color map
    """
    color_dict = {}
    for v in third_values:
        color_dict[v] = '#%06X' % randint(0, 0xFFFFFF)
    return color_dict


def apply(points_list: List[Any], attributes: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None):
    """
    Creates the dotted chart with the event stream and the provided attributes

    Parameters
    ---------------
    points_list
        List of points (event stream)
    attributes
        List of attributes that should be included in the dotted chart
    parameters
        Parameters of the visualization, including:
        - Parameters.FORMAT => the format of the visualization (svg, png, ...)
        - Parameters.DOT_SIZE => the size of the dot in the dotted chart

    Returns
    ---------------
    file_path
        Path to the dotted chart visualization
    """
    if parameters is None:
        parameters = {}

    if attributes is None or len(attributes) < 2:
        raise Exception("dotted chart requires the specification of at least two attributes")
    elif len(attributes) > 3:
        raise Exception("dotted chart requires the specification of at most three attributes")

    format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    dot_size = exec_utils.get_param_value(Parameters.DOT_SIZE, parameters, 0.07)

    unique_values = __build_unique_values(points_list)
    corr_dict, attr_type = __build_corr_dict(unique_values)
    color_dict = __build_color_dict(unique_values[2]) if len(attributes) == 3 else None

    x_length = 10
    y_length = 10
    if attr_type[0] == "str":
        x_length = max(x_length, len(unique_values[0]) * 1.8)
    if attr_type[1] == "str":
        y_length = max(y_length, len(unique_values[1]) * 0.75)

    output_file_gv = tempfile.NamedTemporaryFile(suffix=".gv")
    output_file_gv.close()
    output_file_img = tempfile.NamedTemporaryFile(suffix="." + format)
    output_file_img.close()

    lines = ["graph G {"]
    lines.append("origin [label=\"\", shape=none, width=\"0px\", height=\"0px\", pos=\"0,0!\"];")
    lines.append("rightX [label=\"\", shape=none, width=\"0px\", height=\"0px\", pos=\"%d,0!\"];" % (x_length))
    lines.append("topY [label=\"\", shape=none, width=\"0px\", height=\"0px\", pos=\"0,%d!\"];" % (y_length))
    lines.append("rightXlabel [label=\"%s\", shape=none, width=\"0px\", height=\"0px\", pos=\"%d,0!\"];" % (
        attributes[0], x_length + 1.5))
    lines.append("topYlabel [label=\"%s\", shape=none, width=\"0px\", height=\"0px\", pos=\"0,%d!\"];" % (
        attributes[1], y_length + 1.0))
    lines.append("origin -- rightX [ color=\"black\" ];")
    lines.append("origin -- topY [ color=\"black\" ];")

    if attr_type[0] == "str":
        for k, v in corr_dict[0].items():
            n_id = "n" + str(uuid.uuid4()).replace("-", "") + "e"
            lines.append(
                "%s [label=\"%s\", shape=none, width=\"0px\", height=\"0px\", pos=\"%.10f,0!\", fontsize=\"6pt\"];" % (
                    n_id, str(k), v * x_length))

    if attr_type[1] == "str":
        for k, v in corr_dict[1].items():
            n_id = "n" + str(uuid.uuid4()).replace("-", "") + "e"
            lines.append(
                "%s [label=\"%s\", shape=none, width=\"0px\", height=\"0px\", pos=\"0,%.10f!\", fontsize=\"6pt\"];" % (
                    n_id, str(k), v * y_length))

    for p in points_list:
        coord_x = corr_dict[0][p[0]]
        coord_y = corr_dict[1][p[1]]
        color = color_dict[p[2]] if color_dict is not None else "blue"
        n_id = "n" + str(uuid.uuid4()).replace("-", "") + "e"
        lines.append(
            "%s [label=\"\", shape=circle,  width=\"%.10fpx\", height=\"%.10fpx\", pos=\"%.10f,%.10f!\", fontsize=\"6pt\", style=\"filled\", fillcolor=\"%s\"];" % (
                n_id, dot_size, dot_size, coord_x * x_length, coord_y * y_length, color))

    if color_dict is not None:
        lines.append(
            "Legend [label=\"legend (attribute: %s)\", shape=none, width=\"0px\", height=\"0px\", pos=\"0,-1!\"]" % (
                attributes[2]))
        row = -1
        for k, v in color_dict.items():
            row -= 1
            n_id = "n" + str(uuid.uuid4()).replace("-", "") + "e"
            lines.append(
                "%s [label=\"\", shape=circle, width=\"%.10fpx\", height=\"%.10fpx\", fontsize=\"6pt\", style=\"filled\", fillcolor=\"%s\", pos=\"0,%d!\"]" % (
                    n_id, dot_size, dot_size, v, row))
            n_id = "n" + str(uuid.uuid4()).replace("-", "") + "e"
            lines.append(
                "%s [label=\"%s\", shape=none, width=\"0px\", height=\"0px\", pos=\"1.5,%d!\", fontsize=\"9pt\"];" % (
                    n_id, str(k), row))

    lines.append("}")

    lines = "\n".join(lines)

    F = open(output_file_gv.name, "w")
    F.write(lines)
    F.close()

    os.system("neato -T" + format + " " + output_file_gv.name + " > " + output_file_img.name)

    return output_file_img.name
