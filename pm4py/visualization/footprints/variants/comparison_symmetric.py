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
from graphviz import Source
import tempfile
from pm4py.util import exec_utils
from enum import Enum
from typing import Optional, Dict, Any, Union


class Parameters(Enum):
    FORMAT = "format"


UNKNOWN_SYMBOL = "&#63;"
XOR_SYMBOL = "&#35;"
PREV_SYMBOL = "&#60;"
SEQUENCE_SYMBOL = "&#62;"
PARALLEL_SYMBOL = "||"


def apply(fp1: Dict[str, Any], fp2: Dict[str, Any], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Source:
    """
    Visualize a comparison between two footprint tables

    Parameters
    ---------------
    fp1
        Footprints associated to the log (NOT a list)
    fp2
        Footprints associated to the model
    parameters
        Parameters of the algorithm, including:
            - Parameters.FORMAT => Format of the visualization

    Returns
    ---------------
    gviz
        Graphviz object
    """
    if parameters is None:
        parameters = {}

    if type(fp1) is list or type(fp2) is list:
        raise Exception("footprints visualizer does not work on list of footprints!")

    activities1 = sorted(list(set(x[0] for x in fp1["sequence"]).union(set(x[1] for x in fp1["sequence"])).union(
        set(x[0] for x in fp1["parallel"])).union(set(x[1] for x in fp1["parallel"]))))
    activities2 = sorted(list(set(x[0] for x in fp2["sequence"]).union(set(x[1] for x in fp2["sequence"])).union(
        set(x[0] for x in fp2["parallel"])).union(set(x[1] for x in fp2["parallel"]))))
    activities = sorted(list(set(activities1).union(set(activities2))))
    fp_table = {}

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    filename.close()

    footprints_table = ["digraph {\n", "tbl [\n", "shape=plaintext\n", "label=<\n"]
    footprints_table.append("<table border='0' cellborder='1' color='blue' cellspacing='0'>\n")

    footprints_table.append("<tr><td></td>")
    for act in activities:
        footprints_table.append("<td><b>"+act+"</b></td>")
    footprints_table.append("</tr>\n")

    for a1 in activities:
        footprints_table.append("<tr><td><b>"+a1+"</b></td>")
        for a2 in activities:
            symb_1 = "?"
            symb_2 = "?"

            if a1 in activities1 and a2 in activities1:
                symb_1 = XOR_SYMBOL
                if (a1, a2) in fp1["parallel"]:
                    symb_1 = PARALLEL_SYMBOL
                elif (a1, a2) in fp1["sequence"]:
                    symb_1 = SEQUENCE_SYMBOL
                elif (a2, a1) in fp1["sequence"]:
                    symb_1 = PREV_SYMBOL

            if a1 in activities2 and a2 in activities2:
                symb_2 = XOR_SYMBOL
                if (a1, a2) in fp2["parallel"]:
                    symb_2 = PARALLEL_SYMBOL
                elif (a1, a2) in fp2["sequence"]:
                    symb_2 = SEQUENCE_SYMBOL
                elif (a2, a1) in fp2["sequence"]:
                    symb_2 = PREV_SYMBOL

            if symb_1 == symb_2:
                footprints_table.append("<td><font color=\"black\">"+symb_1+"</font></td>")
            else:
                footprints_table.append("<td><font color=\"red\">"+symb_1+"&nbsp;&nbsp;"+symb_2+"</font></td>")
        footprints_table.append("</tr>\n")

    footprints_table.append("</table>\n")
    footprints_table.append(">];\n")
    footprints_table.append("}\n")

    footprints_table = "".join(footprints_table)

    gviz = Source(footprints_table, filename=filename.name)
    gviz.format = image_format

    return gviz
